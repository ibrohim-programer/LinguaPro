from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification, BroadcastNotification
from django.contrib.auth import get_user_model

User = get_user_model()

MAX_NOTIFICATIONS = 30  # Har bir foydalanuvchi uchun maksimum xabar soni


def _trim_old_notifications(user):
    """
    Foydalanuvchining xabarlari 30 dan oshsa,
    eng eski xabarlarni o'chirib, faqat yangi 30 tasini qoldiradi.
    """
    qs = Notification.objects.filter(recipient=user).order_by('-created_at')
    if qs.count() > MAX_NOTIFICATIONS:
        keep_ids = list(qs.values_list('id', flat=True)[:MAX_NOTIFICATIONS])
        Notification.objects.filter(recipient=user).exclude(
            id__in=keep_ids
        ).delete()


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

    # Har bir foydalanuvchi uchun 30 dan oshgan eski xabarlarni o'chir
    for user in users:
        _trim_old_notifications(user)

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