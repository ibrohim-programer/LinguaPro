from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

from .models import Group , GroupStudent 


WEEK_DAYS_MAP = {
    'toq_kunlar': [0, 2, 4],   
    'juft_kunlar': [1, 3, 5],   
    'har_kuni': [0, 1, 2, 3, 4, 5],
}

# Kunlarni matn ko'rinishida chiqarish uchun
WEEK_DAYS_NAMES = {
    0: "Dushanba", 1: "Seshanba", 2: "Chorshanba",
    3: "Payshanba", 4: "Juma", 5: "Shanba"
}

# Hafta kunlari turini aniqlash uchun teskari map
WEEK_DAYS_TYPE_LABELS = {
    (0, 2, 4): 'Toq kunlar',
    (1, 3, 5): 'Juft kunlar',
    (0, 1, 2, 3, 4, 5): 'Har kuni',
}


class GroupSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='teacher'))
    
    # Kategoriya tanlash uchun (Faqat POST/PUT uchun)
    week_days_type = serializers.ChoiceField(
        choices=[(k, k.replace('_', ' ').capitalize()) for k in WEEK_DAYS_MAP.keys()],
        write_only=True,
        required=True  # Majburiy tanlanishi uchun
    )
    
    # GET qilganda kunlarni nomini chiqarish uchun
    week_days_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Group
        fields = [
            'id', 'name', 'course', 'teacher',
            'start_time', 'end_time',
            'week_days_type',    # Input uchun
            'week_days',         # Read-only (ID list: [0, 2, 4])
            'week_days_display', # Read-only (Nomlar: "Dushanba, Chorshanba...")
            'status', 'start_date', 'end_date', 'created_at',
        ]
        extra_kwargs = {
            'week_days': {'read_only': True}
        }

    def validate(self, attrs):
        week_type = attrs.pop('week_days_type', None)
        if week_type in WEEK_DAYS_MAP:
            attrs['week_days'] = WEEK_DAYS_MAP[week_type]
        return super().validate(attrs)

    def get_week_days_display(self, obj):
        if not obj.week_days:
            return ""
        days_list = sorted(obj.week_days)
        return ", ".join([WEEK_DAYS_NAMES.get(day, "") for day in days_list])
    
    
class AddStudentSerializer(serializers.Serializer):
    username = serializers.CharField()
    
    def validate_username(self , value):
        try:
            user = User.objects.get(username=value, role='student')
        except User.DoesNotExist:
            raise serializers.ValidationError("Bunday student topilmadi!")
        return value


# Student ma'lumotlarini chiqaruvchi serializer
class StudentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']


# GroupStudent serializer
class GroupStudentSerializer(serializers.ModelSerializer):
    username  = serializers.CharField(source='student.username',  read_only=True)
    full_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model  = GroupStudent
        fields = ['id', 'student', 'username', 'full_name', 'joined_at']


class MyGroupSerializer(serializers.ModelSerializer):
    students = GroupStudentSerializer(source='group_students', many=True, read_only=True)

    class Meta:
        model  = Group
        fields = ['id', 'name', 'course', 'teacher', 'status', 'week_days',
                  'start_date', 'start_time', 'end_time', 'students']

        
class AvailableStudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'phone', 'avatar', 'learning_goal']


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
    course_name     = serializers.CharField(source='course.name', read_only=True)
    teacher_name    = serializers.CharField(source='teacher.full_name', read_only=True)
    student_count   = serializers.SerializerMethodField()
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


# ===================== YANGI: Student Dars Jadvali =====================

class StudentScheduleSerializer(serializers.ModelSerializer):
    """
    Student dars jadvalini quyidagi formatda chiqaradi:

        title      : "Kurs nomi - Guruh nomi"
        time       : "08:00 - 10:00"
        week_days_type  : "Toq kunlar"  /  "Juft kunlar"  /  "Har kuni"  /  "Maxsus"
        week_days_names : ["Dushanba", "Chorshanba", "Juma"]
    """
    # "Python kursi - A-guruh"  ko'rinishidagi sarlavha
    title = serializers.SerializerMethodField()

    # "08:00 - 10:00"  ko'rinishidagi vaqt
    time = serializers.SerializerMethodField()

    # "Toq kunlar" / "Juft kunlar" / "Har kuni" / "Maxsus"
    week_days_type = serializers.SerializerMethodField()

    # ["Dushanba", "Chorshanba", "Juma"]
    week_days_names = serializers.SerializerMethodField()

    class Meta:
        model  = Group
        fields = [
            'id',
            'title',           # "Kurs nomi - Guruh nomi"
            'time',            # "08:00 - 10:00"
            'week_days_type',  # "Toq kunlar"
            'week_days_names', # ["Dushanba", "Chorshanba", "Juma"]
            'status',
            'start_date',
            'end_date',
        ]

    def get_title(self, obj):
        course_name = obj.course.name if obj.course else 'Kurs nomi yo\'q'
        return f"{course_name} - {obj.name}"

    def get_time(self, obj):
        # TimeField -> "HH:MM" formatiga o'giramiz
        start = obj.start_time.strftime('%H:%M') if obj.start_time else '--:--'
        end   = obj.end_time.strftime('%H:%M')   if obj.end_time   else '--:--'
        return f"{start} - {end}"

    def get_week_days_type(self, obj):
        days = tuple(sorted(obj.week_days or []))
        return WEEK_DAYS_TYPE_LABELS.get(days, 'Maxsus')

    def get_week_days_names(self, obj):
        days = sorted(obj.week_days or [])
        return [WEEK_DAYS_NAMES.get(d, '') for d in days]

# ======================================================================