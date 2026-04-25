from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status, serializers as rf_serializers

from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer

from django.shortcuts import get_object_or_404
from django.db.models import Max, Count, Q

from apps.groups.models import Group, GroupStudent
from .models import GroupMessage
from .serializers import GroupMessageSerializer, SendMessageSerializer
from apps.common.permissions import IsGroupMember, is_group_member


# ─────────────────────────────────────────────
#  Inline serializer — guruh ro'yxati uchun
# ─────────────────────────────────────────────
class LastMessageSerializer(rf_serializers.Serializer):
    content    = rf_serializers.CharField(allow_null=True)
    type       = rf_serializers.CharField(allow_null=True)
    sender     = rf_serializers.CharField(allow_null=True)
    created_at = rf_serializers.DateTimeField(allow_null=True)


class ChatGroupSerializer(rf_serializers.Serializer):
    id           = rf_serializers.IntegerField()
    name         = rf_serializers.CharField()
    status       = rf_serializers.CharField()
    unread_count = rf_serializers.IntegerField()
    last_message = LastMessageSerializer(allow_null=True)


class PaginatedMessageSerializer(rf_serializers.Serializer):
    count     = rf_serializers.IntegerField()
    page      = rf_serializers.IntegerField()
    page_size = rf_serializers.IntegerField()
    results   = GroupMessageSerializer(many=True)


# ─────────────────────────────────────────────
#  1. Mening guruhlarim (chat panel)
# ─────────────────────────────────────────────
@extend_schema(
    tags=['Messages'],
    summary='Mening guruhlarim (chat uchun)',
    responses={200: ChatGroupSerializer(many=True)},
)
class MyGroupListView(ListAPIView):
    """
    GET /api/messages/groups/
    """
    permission_classes = [IsAuthenticated]
    # ✅ spectacular uchun serializer_class qo'yildi
    serializer_class   = ChatGroupSerializer

    def get_queryset(self):
        # ✅ swagger_fake_view tekshiruvi
        if getattr(self, 'swagger_fake_view', False):
            return Group.objects.none()

        user = self.request.user
        role = getattr(user, 'role', None)

        if role == 'teacher':
            qs = Group.objects.filter(teacher=user)
        elif role == 'student':
            qs = Group.objects.filter(group_students__student=user)
        else:
            qs = Group.objects.all()

        return qs.annotate(
            last_message_at=Max('messages__created_at'),
            unread_count=Count('messages', filter=~Q(messages__read_by=user))
        ).order_by('-last_message_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        for group in queryset:
            last_msg = group.messages.order_by('-created_at').first()
            data.append({
                'id':           group.id,
                'name':         group.name,
                'status':       group.status,
                'unread_count': getattr(group, 'unread_count', 0),
                'last_message': {
                    'content':    last_msg.content if last_msg else None,
                    'type':       last_msg.message_type if last_msg else None,
                    'sender':     last_msg.sender.get_full_name() if last_msg else None,
                    'created_at': last_msg.created_at if last_msg else None,
                } if last_msg else None,
            })
        return Response(data)


# ─────────────────────────────────────────────
#  2. Guruh xabarlari ro'yxati
# ─────────────────────────────────────────────
@extend_schema(
    tags=['Messages'],
    summary='Guruh xabarlari',
    parameters=[
        OpenApiParameter('group_id',  int, OpenApiParameter.PATH),
        OpenApiParameter('page',      int, OpenApiParameter.QUERY, default=1),
        OpenApiParameter('page_size', int, OpenApiParameter.QUERY, default=50),
    ],
    responses={
        200: PaginatedMessageSerializer,
        403: inline_serializer('ForbiddenError', fields={'detail': rf_serializers.CharField()}),
    }
)
class GroupMessageListView(APIView):
    """
    GET /api/messages/groups/{group_id}/messages/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)

        if not is_group_member(request.user, group):
            return Response(
                {'detail': 'Siz bu guruhning a\'zosi emassiz!'},
                status=status.HTTP_403_FORBIDDEN
            )

        page      = max(int(request.query_params.get('page', 1)), 1)
        page_size = min(int(request.query_params.get('page_size', 50)), 100)
        offset    = (page - 1) * page_size

        messages = GroupMessage.objects.filter(group=group)\
                               .select_related('sender')\
                               .prefetch_related('read_by')

        total    = messages.count()
        messages = messages[offset: offset + page_size]

        for msg in messages:
            msg.read_by.add(request.user)

        serializer = GroupMessageSerializer(messages, many=True, context={'request': request})
        return Response({
            'count':     total,
            'page':      page,
            'page_size': page_size,
            'results':   serializer.data,
        })


# ─────────────────────────────────────────────
#  3. Xabar yuborish
# ─────────────────────────────────────────────
@extend_schema(
    tags=['Messages'],
    summary='Guruhga xabar yuborish',
    request=SendMessageSerializer,
    responses={
        201: GroupMessageSerializer,
        403: inline_serializer('SendForbidden', fields={'detail': rf_serializers.CharField()}),
    }
)
class SendGroupMessageView(APIView):
    """
    POST /api/messages/groups/{group_id}/send/
    """
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)

        if not is_group_member(request.user, group):
            return Response(
                {'detail': 'Siz bu guruhning a\'zosi emassiz!'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data       = serializer.validated_data
        attachment = data.get('attachment')
        image      = data.get('image')

        if image:
            msg_type = GroupMessage.MessageType.IMAGE
        elif attachment:
            msg_type = GroupMessage.MessageType.FILE
        else:
            msg_type = GroupMessage.MessageType.TEXT

        message = GroupMessage.objects.create(
            group        = group,
            sender       = request.user,
            content      = data.get('content'),
            attachment   = attachment,
            image        = image,
            message_type = msg_type,
        )
        message.read_by.add(request.user)

        return Response(
            GroupMessageSerializer(message, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


# ─────────────────────────────────────────────
#  4. Xabarni o'chirish
# ─────────────────────────────────────────────
@extend_schema(
    tags=['Messages'],
    summary='Xabarni o\'chirish',
    responses={
        200: inline_serializer('DeleteMsgOk',  fields={'detail': rf_serializers.CharField()}),
        403: inline_serializer('DeleteMsgForbidden', fields={'detail': rf_serializers.CharField()}),
    }
)
class DeleteGroupMessageView(APIView):
    """
    DELETE /api/messages/groups/{group_id}/messages/{message_id}/
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, group_id, message_id):
        group   = get_object_or_404(Group, pk=group_id)
        message = get_object_or_404(GroupMessage, pk=message_id, group=group)

        if not is_group_member(request.user, group):
            return Response(
                {'detail': 'Siz bu guruhning a\'zosi emassiz!'},
                status=status.HTTP_403_FORBIDDEN
            )

        is_admin = getattr(request.user, 'role', None) == 'admin' or request.user.is_staff
        if message.sender != request.user and not is_admin:
            return Response(
                {'detail': 'Faqat o\'zingizning xabarini o\'chira olasiz!'},
                status=status.HTTP_403_FORBIDDEN
            )

        message.delete()
        return Response({'detail': 'Xabar o\'chirildi!'}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────
#  5. O'qilmagan xabarlar soni
# ─────────────────────────────────────────────
@extend_schema(
    tags=['Messages'],
    summary='O\'qilmagan xabarlar soni',
    responses={
        200: inline_serializer('UnreadCount', fields={'unread_count': rf_serializers.IntegerField()}),
    }
)
class UnreadCountView(APIView):
    """
    GET /api/messages/unread-count/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, 'role', None)

        if role == 'teacher':
            groups = Group.objects.filter(teacher=user)
        elif role == 'student':
            groups = Group.objects.filter(group_students__student=user)
        else:
            groups = Group.objects.all()

        total_unread = GroupMessage.objects.filter(
            group__in=groups
        ).exclude(read_by=user).count()

        return Response({'unread_count': total_unread})