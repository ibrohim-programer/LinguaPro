from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import GroupMessage

User = get_user_model()


class SenderSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'username', 'full_name', 'role']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class GroupMessageSerializer(serializers.ModelSerializer):
    sender       = SenderSerializer(read_only=True)
    is_read      = serializers.SerializerMethodField()
    read_count   = serializers.SerializerMethodField()
    file_url     = serializers.SerializerMethodField()
    image_url    = serializers.SerializerMethodField()

    class Meta:
        model  = GroupMessage
        fields = [
            'id', 'group', 'sender',
            'content', 'message_type',
            'file_url', 'image_url',
            'is_read', 'read_count',
            'created_at',
        ]
        read_only_fields = ['id', 'sender', 'created_at', 'group']

    def get_is_read(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_read_by_user(request.user)
        return False

    def get_read_count(self, obj):
        return obj.read_by.count()

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.attachment and request:
            return request.build_absolute_uri(obj.attachment.url)
        return None

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class SendMessageSerializer(serializers.ModelSerializer):
    """
    POST /conversations/{group_id}/send/ uchun serializer.
    Foydalanuvchi matn, fayl yoki rasm yuborishi mumkin.
    """
    class Meta:
        model  = GroupMessage
        fields = ['content', 'attachment', 'image']

    def validate(self, attrs):
        content    = attrs.get('content')
        attachment = attrs.get('attachment')
        image      = attrs.get('image')

        if not content and not attachment and not image:
            raise serializers.ValidationError(
                "Matn, fayl yoki rasm — kamida bittasini yuboring!"
            )
        # Bir vaqtda fayl ham rasm ham bo'lmasin
        if attachment and image:
            raise serializers.ValidationError(
                "Bir xabarda fayl va rasm birgalikda bo'lmaydi!"
            )
        return attrs

    def validate_image(self, value):
        if value:
            allowed = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if hasattr(value, 'content_type') and value.content_type not in allowed:
                raise serializers.ValidationError(
                    "Faqat JPEG, PNG, GIF, WEBP formatdagi rasmlar!"
                )
            max_size = 10 * 1024 * 1024  # 10 MB
            if value.size > max_size:
                raise serializers.ValidationError("Rasm hajmi 10MB dan oshmasin!")
        return value

    def validate_attachment(self, value):
        if value:
            max_size = 50 * 1024 * 1024  # 50 MB
            if value.size > max_size:
                raise serializers.ValidationError("Fayl hajmi 50MB dan oshmasin!")
        return value
    