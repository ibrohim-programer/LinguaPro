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

    class Meta:
        model = Submission
        fields = ['id','assignment','assignment_title','student','text_answer','file_answer','score','submitted_at',]
        read_only_fields = ['student', 'submitted_at', 'score']


class GradeSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['score']