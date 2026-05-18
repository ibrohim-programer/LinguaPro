from rest_framework import serializers
from .models import Assignment, Submission


class AssignmentSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Assignment
        fields = ['id','title','description','group','created_by','deadline','max_score','attachment','submission_type',"is_active",'created_at']
        read_only_fields = ['created_by', 'created_at',"is_active"]

class SubmissionSerializer(serializers.ModelSerializer):
    student = serializers.ReadOnlyField(source='student.user.username')
    assignment_title = serializers.ReadOnlyField(source='assignment.title')
    is_submitted = serializers.BooleanField(default=True, read_only=True)

    class Meta:
        model = Submission
        fields = [
            'id', 'assignment', 'assignment_title', 'student',
            'text_answer', 'file_answer', 'score', 'submitted_at',
            'is_submitted',   # ← QO'SHILDI
        ]
        read_only_fields = ['student', 'submitted_at', 'score']

    # def get_is_submitted(self, obj):   # ← QO'SHILDI
    #     return obj.pk is not None


class GradeSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['score']
        
        
# Mavjud kodga QO'SHILADI (oxiriga)

class StudentSubmissionStatusSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField()
    status = serializers.CharField()   
    submitted_at = serializers.DateTimeField(allow_null=True)
    score = serializers.IntegerField(allow_null=True)
    text_answer = serializers.CharField(allow_null=True)
    file_answer = serializers.FileField(allow_null=True)