from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

from .models import Group , GroupStudent 


WEEK_DAYS_MAP = {
    'toq_kunlar':  [0, 2, 4],              # Du, Ch, Ju
    'juft_kunlar': [1, 3, 5],              # Se, Pa, Sh
    'har_kuni':    [0, 1, 2, 3, 4, 5, 6], # Hamma kun
}

class GroupSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='teacher'))
    
    # Faqat yozish uchun (POST/PUT)
    week_days_type = serializers.ChoiceField(
        choices=list(WEEK_DAYS_MAP.keys()),
        write_only=True,
        required=False,
    )
    # Faqat o'qish uchun (GET) — week_days dan qayta hisoblaydi
    week_days_label = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = Group
        fields = [
            'id', 'name', 'course', 'teacher',
            'start_time', 'end_time',
            'week_days_type',   # <-- input (POST/PUT)
            'week_days',        # <-- saqlangan list (GET)
            'week_days_label',  # <-- "Toq kunlar" (GET)
            'status', 'start_date', 'end_date', 'created_at',
        ]

    def validate(self, attrs):
        week_days_type = attrs.pop('week_days_type', None)
        if week_days_type:
            attrs['week_days'] = WEEK_DAYS_MAP[week_days_type]
        return super().validate(attrs)

    def get_week_days_label(self, obj):
        days = sorted(obj.week_days or [])
        labels = {
            (0, 2, 4): 'Toq kunlar',
            (1, 3, 5): 'Juft kunlar',
            (0, 1, 2, 3, 4, 5, 6): 'Har kuni',
        }
        return labels.get(tuple(days), 'Maxsus')
    
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

# Student ma'lumotlarini chiqaruvchi serializer
class StudentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User  # yoki Student model
        fields = ['id', 'username', 'full_name']


# GroupStudent serializer
class GroupStudentSerializer(serializers.ModelSerializer):
    username  = serializers.CharField(source='student.username',  read_only=True)
    full_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model  = GroupStudent
        fields = ['id', 'student', 'username', 'full_name', 'joined_at']    
class MyGroupSerializer(serializers.ModelSerializer):
    students = GroupStudentSerializer( source = 'group_students' , many = True , read_only = True)
    class Meta:
        model  = Group
        fields = ['id', 'name', 'course', 'teacher', 'status', 'start_date','start_time','end_time', 'students', ]
  
    
        
class AvailableStudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id' , 'username',"full_name","phone","avatar","learning_goal"]


WEEKDAY_NAMES = {
    '0': 'Dushanba', '1': 'Seshanba', '2': 'Chorshanba',
    '3': 'Payshanba', '4': 'Juma', '5': 'Shanba', '6': 'Yakshanba',
}


class TodayScheduleSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()
    lesson_status = serializers.SerializerMethodField()
    course_name   = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model  = Group
        fields = [
            'id', 'name', 'course_name', 'start_time', 'end_time',
            'student_count', 'lesson_status',
        ]

    def get_student_count(self, obj):
        return obj.group_students.count()

    def get_lesson_status(self, obj):
        mode = self.context.get('date_mode', 'today')

        if mode == 'past':
            return 'completed'
        if mode == 'future':
            return 'upcoming'

        # today — haqiqiy vaqt bilan taqqoslaymiz
        now = self.context.get('now')
        if now is None:
            return 'upcoming'

        start = obj.start_time
        end   = obj.end_time

        if now < start:
            return 'upcoming'
        elif start <= now <= end:
            return 'ongoing'
        else:
            return 'completed'  

class StudentMyGroupSerializer(serializers.ModelSerializer):
    """Student o'z guruhini ko'radi — boshqa studentlar ko'rsatilmaydi"""
    course_name    = serializers.CharField(source='course.name', read_only=True)
    teacher_name   = serializers.CharField(source='teacher.full_name', read_only=True)
    student_count  = serializers.SerializerMethodField()
    week_days_label = serializers.SerializerMethodField()

    class Meta:
        model  = Group
        fields = [
            'id', 'name',
            'course_name', 'teacher_name',
            'start_time', 'end_time',
            'week_days', 'week_days_label',
            'status', 'start_date', 'end_date',
            'student_count',
        ]

    def get_student_count(self, obj):
        return obj.group_students.count()

    def get_week_days_label(self, obj):
        days = sorted(obj.week_days or [])
        labels = {
            (0, 2, 4): 'Toq kunlar (Du, Ch, Ju)',
            (1, 3, 5): 'Juft kunlar (Se, Pa, Sh)',
            (0, 1, 2, 3, 4, 5, 6): 'Har kuni',
        }
        return labels.get(tuple(days), 'Maxsus')
