from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

from .models import Group , GroupStudent 


class GroupSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset = User.objects.filter(role = 'teacher'))
    class Meta:
        model = Group
        fields = ['id',"name","course","teacher","start_time","end_time","week_days","status","start_date","end_date","created_at",]
        
    def validate(self, attrs):
        return super().validate(attrs)
    
class GroupStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = GroupStudent
        fields = ['id', 'student', 'joined_at']
        
class AddStudentSerializer(serializers.Serializer):
    username = serializers.CharField()
    
    def validate_username(self , value):
        try:
            user = User.objects.get(username = value , role = 'student')
        except User.DoesNotExist:
            raise serializers.ValidationError("Bunday student topilmadi!")
        return value

class MyGroupSerializer(serializers.ModelSerializer):
    students = GroupStudentSerializer(source = 'group_students' , many = True , read_only = True)
    class Meta:
        model  = Group
        fields = ['id', 'name', 'course', 'teacher', 'status', 'start_date','start_time','end_time', 'students']
        
        
class AvailableStudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id' , 'username',"phone","avatar","learning_goal"]
        
    