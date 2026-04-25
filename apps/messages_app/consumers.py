import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class GroupChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket: ws://domain/ws/chat/{group_id}/

    Event turlari (type field):
      client → server:
        { "type": "chat.message", "content": "...", "message_type": "text" }
        { "type": "chat.read",    "message_id": 5 }
        { "type": "chat.typing"  }

      server → client:
        { "type": "chat.message",  ...message data... }
        { "type": "chat.read",     "message_id": 5, "user_id": 3 }
        { "type": "chat.typing",   "user_id": 3, "username": "..." }
        { "type": "chat.error",    "detail": "..." }
        { "type": "chat.online",   "user_id": 3 }
        { "type": "chat.offline",  "user_id": 3 }
    """

    # ──────────────────────────────────────────
    #  Connect / Disconnect
    # ──────────────────────────────────────────
    async def connect(self):
        self.group_id   = self.scope['url_route']['kwargs']['group_id']
        self.room_group = f'chat_group_{self.group_id}'
        self.user       = self.scope.get('user')

        # Auth tekshiruvi
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        # Guruh a'zosi ekanini tekshir
        is_member = await self._is_member()
        if not is_member:
            await self.close(code=4003)
            return

        # Channel layerga qo'shish
        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

        # Boshqalarga "online" xabar yuborish
        await self.channel_layer.group_send(
            self.room_group,
            {
                'type':    'chat_online',
                'user_id': self.user.pk,
                'username': self.user.username,
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group') and self.user and self.user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group,
                {
                    'type':    'chat_offline',
                    'user_id': self.user.pk,
                    'username': self.user.username,
                }
            )
            await self.channel_layer.group_discard(self.room_group, self.channel_name)

    # ──────────────────────────────────────────
    #  Receive (client → server)
    # ──────────────────────────────────────────
    async def receive(self, text_data=None, bytes_data=None):
        try:
            data      = json.loads(text_data or '{}')
            event_type = data.get('type', 'chat.message')

            if event_type == 'chat.message':
                await self._handle_message(data)

            elif event_type == 'chat.read':
                await self._handle_read(data)

            elif event_type == 'chat.typing':
                await self._handle_typing()

            else:
                await self._send_error('Noma\'lum event turi!')

        except json.JSONDecodeError:
            await self._send_error('JSON format xatosi!')
        except Exception as e:
            await self._send_error(str(e))

    # ──────────────────────────────────────────
    #  Handler: yangi xabar
    # ──────────────────────────────────────────
    async def _handle_message(self, data):
        content      = (data.get('content') or '').strip()
        message_type = data.get('message_type', 'text')

        if not content:
            await self._send_error('Xabar bo\'sh bo\'lmasin!')
            return

        if message_type not in ('text', 'file', 'image'):
            await self._send_error('Noto\'g\'ri message_type!')
            return

        # Faqat text WebSocket orqali — fayl/rasm REST API orqali yuboriladi
        if message_type != 'text':
            await self._send_error(
                'Fayl/rasm yuborish uchun REST API dan foydalaning: '
                'POST /api/messages/groups/{id}/send/'
            )
            return

        # DB ga saqlash
        message = await self._save_message(content)

        # Guruh ichidagi hamma ga yuborish
        await self.channel_layer.group_send(
            self.room_group,
            {
                'type':         'chat_message',
                'message_id':   message['id'],
                'content':      message['content'],
                'message_type': message['message_type'],
                'sender_id':    message['sender_id'],
                'sender_name':  message['sender_name'],
                'sender_role':  message['sender_role'],
                'created_at':   message['created_at'],
            }
        )

    # ──────────────────────────────────────────
    #  Handler: o'qildi
    # ──────────────────────────────────────────
    async def _handle_read(self, data):
        message_id = data.get('message_id')
        if not message_id:
            return

        await self._mark_read(message_id)

        await self.channel_layer.group_send(
            self.room_group,
            {
                'type':       'chat_read',
                'message_id': message_id,
                'user_id':    self.user.pk,
            }
        )

    # ──────────────────────────────────────────
    #  Handler: yozmoqda...
    # ──────────────────────────────────────────
    async def _handle_typing(self):
        await self.channel_layer.group_send(
            self.room_group,
            {
                'type':     'chat_typing',
                'user_id':  self.user.pk,
                'username': self.user.username,
            }
        )

    # ──────────────────────────────────────────
    #  Channel layer → WebSocket yuboruvchilar
    # ──────────────────────────────────────────
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type':         'chat.message',
            'message_id':   event['message_id'],
            'content':      event['content'],
            'message_type': event['message_type'],
            'sender_id':    event['sender_id'],
            'sender_name':  event['sender_name'],
            'sender_role':  event['sender_role'],
            'created_at':   event['created_at'],
        }))

    async def chat_read(self, event):
        await self.send(text_data=json.dumps({
            'type':       'chat.read',
            'message_id': event['message_id'],
            'user_id':    event['user_id'],
        }))

    async def chat_typing(self, event):
        # O'zi uchun typing yubormaymiz
        if event['user_id'] == self.user.pk:
            return
        await self.send(text_data=json.dumps({
            'type':     'chat.typing',
            'user_id':  event['user_id'],
            'username': event['username'],
        }))

    async def chat_online(self, event):
        if event['user_id'] == self.user.pk:
            return
        await self.send(text_data=json.dumps({
            'type':     'chat.online',
            'user_id':  event['user_id'],
            'username': event['username'],
        }))

    async def chat_offline(self, event):
        if event['user_id'] == self.user.pk:
            return
        await self.send(text_data=json.dumps({
            'type':     'chat.offline',
            'user_id':  event['user_id'],
            'username': event['username'],
        }))

    # ──────────────────────────────────────────
    #  DB operatsiyalari (sync → async)
    # ──────────────────────────────────────────
    @database_sync_to_async
    def _is_member(self):
        from apps.groups.models import Group, GroupStudent
        try:
            group = Group.objects.get(pk=self.group_id)
        except Group.DoesNotExist:
            return False

        user = self.user
        role = getattr(user, 'role', None)

        if role == 'admin' or user.is_staff:
            return True
        if role == 'teacher':
            return group.teacher_id == user.pk
        if role == 'student':
            return GroupStudent.objects.filter(group=group, student=user).exists()
        return False

    @database_sync_to_async
    def _save_message(self, content):
        from .models import GroupMessage
        from apps.groups.models import Group

        group   = Group.objects.get(pk=self.group_id)
        message = GroupMessage.objects.create(
            group        = group,
            sender       = self.user,
            content      = content,
            message_type = GroupMessage.MessageType.TEXT,
        )
        message.read_by.add(self.user)

        return {
            'id':          message.pk,
            'content':     message.content,
            'message_type': message.message_type,
            'sender_id':   self.user.pk,
            'sender_name': self.user.get_full_name() or self.user.username,
            'sender_role': getattr(self.user, 'role', ''),
            'created_at':  message.created_at.isoformat(),
        }

    @database_sync_to_async
    def _mark_read(self, message_id):
        from .models import GroupMessage
        try:
            msg = GroupMessage.objects.get(pk=message_id, group_id=self.group_id)
            msg.read_by.add(self.user)
        except GroupMessage.DoesNotExist:
            pass

    async def _send_error(self, detail):
        await self.send(text_data=json.dumps({
            'type':   'chat.error',
            'detail': detail,
        }))