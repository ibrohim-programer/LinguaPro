from rest_framework import serializers
from .models import Notification, BroadcastNotification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = ['id', 'title', 'message', 'is_read', 'related_object_id', 'broadcast', 'created_at']
        read_only_fields = fields


class BroadcastCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = BroadcastNotification
        fields = ['id', 'title', 'message', 'target_role']

    def validate_target_role(self, value):
        allowed = [r.value for r in BroadcastNotification.TargetRole]
        if value not in allowed:
            raise serializers.ValidationError(f'Faqat {allowed} qiymatlar.')
        return value


class BroadcastListSerializer(serializers.ModelSerializer):
    sender_name        = serializers.CharField(source='sender.get_full_name', read_only=True)
    notifications_count = serializers.IntegerField(source='notifications.count', read_only=True)

    class Meta:
        model  = BroadcastNotification
        fields = ['id', 'sender_name', 'title', 'message', 'target_role', 'notifications_count', 'created_at']


class MyNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = ['id', 'title', 'message', 'is_read', 'created_at']
        read_only_fields = fields