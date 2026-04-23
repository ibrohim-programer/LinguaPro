from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Notification

User = get_user_model()
class SendNotificationSerializer(serializers.Serializer):
    target_role = serializers.ChoiceField(choices=['teacher', 'student', 'all'],help_text="Kimga yuborilsin: 'teacher', 'student', yoki 'all'")
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = ['id', 'title', 'message', 'is_read', 'created_at']