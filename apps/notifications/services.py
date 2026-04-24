from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification, BroadcastNotification
from django.contrib.auth import get_user_model
User = get_user_model()

def get_target_users(target_role: str):
    if target_role == BroadcastNotification.TargetRole.ALL:
        return User.objects.filter(is_active=True)
    return User.objects.filter(role=target_role, is_active=True)


def send_broadcast(broadcast: BroadcastNotification):
    users         = get_target_users(broadcast.target_role)
    channel_layer = get_channel_layer()

    notifications = [
        Notification(
            recipient = user,
            title     = broadcast.title,
            message   = broadcast.message,
            broadcast = broadcast,
        )
        for user in users
    ]
    Notification.objects.bulk_create(notifications)

    payload = {
        'type'        : 'send_notification',
        'id'          : broadcast.id,
        'title'       : broadcast.title,
        'message'     : broadcast.message,
        'is_read'     : False,
        'created_at'  : broadcast.created_at.isoformat(),
        'broadcast_id': broadcast.id,
    }

    if broadcast.target_role == BroadcastNotification.TargetRole.ALL:
        async_to_sync(channel_layer.group_send)('notifications_all', payload)

    elif broadcast.target_role == BroadcastNotification.TargetRole.TEACHER:
        async_to_sync(channel_layer.group_send)('notifications_role_teacher', payload)

    elif broadcast.target_role == BroadcastNotification.TargetRole.STUDENT:
        async_to_sync(channel_layer.group_send)('notifications_role_student', payload)