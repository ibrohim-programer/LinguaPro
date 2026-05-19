from rest_framework import serializers
from .models import Assignment, Submission


class AssignmentSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    attachment_url = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description', 'group', 'created_by',
            'deadline', 'max_score', 'attachment', 'attachment_url',
            'submission_type', 'is_active', 'created_at',
        ]
        read_only_fields = ['created_by', 'created_at', 'is_active']

    def get_attachment_url(self, obj):
        request = self.context.get('request')
        if obj.attachment and request:
            return request.build_absolute_uri(obj.attachment.url)
        return None


class SubmissionSerializer(serializers.ModelSerializer):
    # BUG FIX: source='student.username' edi (student.user.username xato edi)
    student = serializers.ReadOnlyField(source='student.username')
    assignment_title = serializers.ReadOnlyField(source='assignment.title')
    is_submitted = serializers.BooleanField(default=True, read_only=True)
    # BUG FIX: absolute URL qaytaradi (avval null kelardi)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = [
            'id', 'assignment', 'assignment_title', 'student',
            'text_answer', 'file_answer', 'file_url',
            'score', 'submitted_at', 'is_submitted',
        ]
        read_only_fields = ['student', 'submitted_at', 'score', 'file_url']
        extra_kwargs = {
            # POST da file_answer optional — file_path orqali ham yuborish mumkin
            'file_answer': {'required': False, 'allow_null': True},
        }

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file_answer and request:
            return request.build_absolute_uri(obj.file_answer.url)
        return None


class GradeSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['score']


# ─────────────────────────────────────────────
#  YANGI: Fayl yuklash uchun serializer
# ─────────────────────────────────────────────
class FileUploadSerializer(serializers.Serializer):
    """POST /assignments/upload/ — fayl yuklash va URL olish."""
    file = serializers.FileField(
        help_text='Yuklanadigan fayl (max 50MB)'
    )

    def validate_file(self, value):
        max_size = 50 * 1024 * 1024  # 50 MB
        if value.size > max_size:
            raise serializers.ValidationError('Fayl hajmi 50MB dan oshmasin!')
        return value


class FileUploadResponseSerializer(serializers.Serializer):
    """Yuklangan faylning URL va path ni qaytaradi."""
    file_path = serializers.CharField(
        help_text='Submission yuborishda shu qiymatni yuboring'
    )
    file_url  = serializers.URLField(
        help_text='Faylni ochish uchun to\'liq URL'
    )
    file_name = serializers.CharField()
    file_size = serializers.IntegerField(help_text='Bayt hisobida')


# ─────────────────────────────────────────────
#  O'ZGARGAN: file_answer → CharField (URL string uchun)
# ─────────────────────────────────────────────
class StudentSubmissionStatusSerializer(serializers.Serializer):
    student_id   = serializers.IntegerField()
    username     = serializers.CharField()
    full_name    = serializers.CharField()
    status       = serializers.CharField()
    submitted_at = serializers.DateTimeField(allow_null=True)
    score        = serializers.IntegerField(allow_null=True)
    text_answer  = serializers.CharField(allow_null=True)
    # BUG FIX: FileField → CharField (view allaqachon .url string beradi)
    file_url     = serializers.CharField(allow_null=True)