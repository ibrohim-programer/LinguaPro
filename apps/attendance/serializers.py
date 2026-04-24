from rest_framework import serializers
from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    group_name   = serializers.CharField(source='group.name', read_only=True)
    marked_by_name = serializers.CharField(source='marked_by.get_full_name', read_only=True)

    class Meta:
        model  = Attendance
        fields = ['id','student','student_name','group','group_name','date','status','note','marked_by','marked_by_name','created_at',]
        read_only_fields = ['id', 'marked_by', 'created_at']

    def validate(self, attrs):
        student = attrs.get('student')
        group = attrs.get('group')
        date = attrs.get('date')
        instance = self.instance

        qs = Attendance.objects.filter(student=student, group=group, date=date)
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Bu o'quvchi uchun bu kunda davomat allaqachon belgilangan.")
        return attrs


class AttendanceStatsSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    group_name = serializers.CharField()
    total = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    late = serializers.IntegerField()
    present_pct = serializers.FloatField()
    absent_pct = serializers.FloatField()
    late_pct = serializers.FloatField()


class MyAttendanceSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model  = Attendance
        fields = ['id', 'group', 'group_name', 'date', 'status', 'note', 'created_at']
        read_only_fields = fields