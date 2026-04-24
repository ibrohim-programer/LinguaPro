import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope['user']

        if not user or not user.is_authenticated:
            await self.close()
            return

        self.user      = user
        self.groups    = []

        # 1) Shaxsiy kanal
        personal_group = f'notifications_user_{user.id}'
        await self.channel_layer.group_add(personal_group, self.channel_name)
        self.groups.append(personal_group)

        # 2) Role guruh kanali
        role_group = f'notifications_role_{user.role}'
        await self.channel_layer.group_add(role_group, self.channel_name)
        self.groups.append(role_group)

        # 3) Umumiy kanal (barchaga)
        await self.channel_layer.group_add('notifications_all', self.channel_name)
        self.groups.append('notifications_all')

        await self.accept()

        unread = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type'        : 'connected',
            'unread_count': unread,
        }))

    async def disconnect(self, close_code):
        for group in getattr(self, 'groups', []):
            await self.channel_layer.group_discard(group, self.channel_name)

    async def receive(self, text_data):
        data   = json.loads(text_data)
        action = data.get('action')

        if action == 'mark_read':
            await self.mark_read(data.get('notification_id'))
            unread = await self.get_unread_count()
            await self.send(text_data=json.dumps({
                'type'           : 'marked_read',
                'notification_id': data.get('notification_id'),
                'unread_count'   : unread,
            }))

        elif action == 'mark_all_read':
            await self.mark_all_read()
            await self.send(text_data=json.dumps({
                'type'        : 'all_marked_read',
                'unread_count': 0,
            }))

    async def send_notification(self, event):
        unread = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type'        : 'new_notification',
            'id'          : event.get('id'),
            'title'       : event.get('title'),
            'message'     : event.get('message'),
            'is_read'     : False,
            'created_at'  : event.get('created_at'),
            'unread_count': unread,
        }))

    @database_sync_to_async
    def get_unread_count(self):
        return Notification.objects.filter(recipient=self.user, is_read=False).count()

    @database_sync_to_async
    def mark_read(self, notification_id):
        Notification.objects.filter(id=notification_id, recipient=self.user).update(is_read=True)

    @database_sync_to_async
    def mark_all_read(self):
        Notification.objects.filter(recipient=self.user, is_read=False).update(is_read=True)