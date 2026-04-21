from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Teacher

User = get_user_model()

class TeacherCreateSerializer(serializers.Serializer):
    username         = serializers.CharField(max_length=50)
    password         = serializers.CharField(write_only=True, min_length=8)
    first_name       = serializers.CharField(max_length=50)
    last_name        = serializers.CharField(max_length=50)
    phone            = serializers.CharField(max_length=15, required=False, allow_blank=True)
    level            = serializers.ChoiceField(choices=Teacher.Level.choices, default=Teacher.Level.Beginner)
    experience_years = serializers.IntegerField(min_value=0, default=0)

    def validate_username(self, value):
        if User.objects.filter(username=value.lower()).exists():
            raise serializers.ValidationError("Bu username band.")
        return value.lower()

    def create(self, validated_data):
        user = User.objects.create_user(
            username   = validated_data['username'],
            password   = validated_data['password'],
            first_name = validated_data['first_name'],
            last_name  = validated_data['last_name'],
            phone      = validated_data.get('phone', ''),
            role       = User.Role.TEACHER,
        )
        teacher = Teacher.objects.create(
            user             = user,
            level            = validated_data.get('level', Teacher.Level.JUNIOR),
            experience_years = validated_data.get('experience_years', 0),
        )
        return teacher


class TeacherListSerializer(serializers.ModelSerializer):
    username         = serializers.CharField(source='user.username')
    full_name        = serializers.CharField(source='user.full_name')
    phone            = serializers.CharField(source='user.phone')
    level_display    = serializers.CharField(source='get_level_display')

    class Meta:
        model  = Teacher
        fields = [
            'id', 'username', 'full_name', 'phone',
            'level', 'level_display', 'experience_years',
            'is_active', 'created_at',
        ]


class TeacherDetailSerializer(serializers.ModelSerializer):
    username         = serializers.CharField(source='user.username')
    full_name        = serializers.CharField(source='user.full_name')
    first_name       = serializers.CharField(source='user.first_name')
    last_name        = serializers.CharField(source='user.last_name')
    phone            = serializers.CharField(source='user.phone')
    level_display    = serializers.CharField(source='get_level_display')

    class Meta:
        model  = Teacher
        fields = [
            'id', 'username', 'full_name', 'first_name', 'last_name', 'phone',
            'level', 'level_display', 'experience_years',
            'is_active', 'created_at',
        ]


class TeacherUpdateSerializer(serializers.Serializer):
    first_name       = serializers.CharField(max_length=50, required=False)
    last_name        = serializers.CharField(max_length=50, required=False)
    phone            = serializers.CharField(max_length=15, required=False, allow_blank=True)
    level            = serializers.ChoiceField(choices=Teacher.Level.choices, required=False)
    experience_years = serializers.IntegerField(min_value=0, required=False)
    is_active        = serializers.BooleanField(required=False)

    def update(self, instance, validated_data):
        user = instance.user

        if 'first_name' in validated_data:
            user.first_name = validated_data['first_name']
        if 'last_name' in validated_data:
            user.last_name = validated_data['last_name']
        if 'phone' in validated_data:
            user.phone = validated_data['phone']
        user.save()

        if 'level' in validated_data:
            instance.level = validated_data['level']
        if 'experience_years' in validated_data:
            instance.experience_years = validated_data['experience_years']
        if 'is_active' in validated_data:
            instance.is_active = validated_data['is_active']
        instance.save()

        return instance