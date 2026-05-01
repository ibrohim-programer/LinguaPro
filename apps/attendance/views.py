from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers as rf_serializers
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Attendance
from .serializers import AttendanceSerializer, MyAttendanceSerializer
from apps.groups.models import Group
from apps.common.permissions import IsStudent, IsAdminOrTeacher


@extend_schema(tags=['Attendance Crud'], summary='Admin - Teacher uchun')
class AttendanceListCreateView(generics.ListCreateAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        qs = Attendance.objects.select_related('student', 'group', 'marked_by')
        group_id = self.request.query_params.get('group')
        date = self.request.query_params.get('date')
        if group_id:
            qs = qs.filter(group_id=group_id)
        if date:
            qs = qs.filter(date=date)
        return qs

    def perform_create(self, serializer):
        serializer.save(marked_by=self.request.user)


@extend_schema(
    tags=['Attendance Crud'],
    summary='Admin - Teacher uchun — Bulk update (1 ta request)',
    request=inline_serializer(
        name='BulkAttendanceUpdateRequest',
        fields={'records': rf_serializers.ListField(child=inline_serializer(name='BulkAttendanceItem',fields={'id':     rf_serializers.IntegerField(),'status': rf_serializers.CharField(),'note':   rf_serializers.CharField(required=False, allow_blank=True),}))}),
    responses={200: AttendanceSerializer(many=True)},)

class AttendanceBulkUpdateView(APIView):
    permission_classes = [IsAdminOrTeacher]
    def put(self, request):
        records = request.data.get('records', [])

        if not records:
            return Response({'detail': "'records' maydoni bo'sh bo'lmasligi kerak."},status=status.HTTP_400_BAD_REQUEST)

        ids = [r.get('id') for r in records if r.get('id') is not None]
        attendance_map = {obj.pk: obj for obj in Attendance.objects.filter(pk__in=ids)}

        errors = []
        to_update = []

        for item in records:
            pk = item.get('id')
            new_status = item.get('status')
            note = item.get('note', None)

            if pk is None:
                errors.append({'id': None, 'detail': "'id' maydoni majburiy."})
                continue

            obj = attendance_map.get(pk)
            if obj is None:
                errors.append({'id': pk, 'detail': f'id={pk} topilmadi.'})
                continue

            allowed = [c[0] for c in Attendance.AttendanceStatus.choices]
            if new_status not in allowed:
                errors.append({'id': pk, 'detail': f"Noto'g'ri status: '{new_status}'. Ruxsat etilganlar: {allowed}"})
                continue

            obj.status = new_status
            obj.marked_by = request.user
            if note is not None:
                obj.note = note
            to_update.append(obj)

        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            Attendance.objects.bulk_update(to_update, fields=['status', 'note', 'marked_by'])

        serializer = AttendanceSerializer(to_update, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['Attendance Crud'], summary='Student uchun')
class MyAttendanceView(generics.ListAPIView):
    serializer_class = MyAttendanceSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Attendance.objects.none()
        return Attendance.objects.filter(student=self.request.user).select_related('group')


@extend_schema(
    tags=['Attendance Crud'],
    summary='Admin - Teacher uchun — Guruh davomatini saqlash (create or update)',
    request=inline_serializer(
        name='GroupAttendanceSaveRequest',
        fields={'date': rf_serializers.DateField(),'records': rf_serializers.ListField(child=inline_serializer(name='GroupAttendanceRecord',fields={'student': rf_serializers.IntegerField(),'status':  rf_serializers.ChoiceField(choices=['present', 'absent', 'late']),'note':    rf_serializers.CharField( required=False, allow_blank=True),})),}),
    responses={200: AttendanceSerializer(many=True)},
)
class AttendanceStatsView(APIView):
    permission_classes = [IsAdminOrTeacher]
    def post(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        date = request.data.get('date')
        records = request.data.get('records', [])
        if not date:
            return Response({'detail': "'date' maydoni majburiy."},status=status.HTTP_400_BAD_REQUEST)
        if not records:
            return Response({'detail': "'records' maydoni bo'sh bo'lmasligi kerak."},status=status.HTTP_400_BAD_REQUEST)

        allowed_statuses = [c[0] for c in Attendance.AttendanceStatus.choices]
        errors = []

        for i, item in enumerate(records):
            if 'student' not in item:
                errors.append({'index': i, 'detail': "'student' maydoni majburiy."})
            if item.get('status') not in allowed_statuses:
                errors.append({'index': i,'detail': f"Noto'g'ri status: '{item.get('status')}'. Ruxsat etilganlar: {allowed_statuses}"})

        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        student_ids = [item['student'] for item in records]
        existing_map = {
            obj.student_id: obj
            for obj in Attendance.objects.filter(group=group,date=date,student_id__in=student_ids)}

        to_create = []
        to_update = []

        for item in records:
            student_id = item['student']
            item_status = item['status']
            note = item.get('note', '')

            if student_id in existing_map:
                obj = existing_map[student_id]
                obj.status = item_status
                obj.note = note
                obj.marked_by = request.user
                to_update.append(obj)
            else:
                to_create.append(Attendance(student_id=student_id,group=group,date=date,status=item_status,note=note,marked_by=request.user,))

        with transaction.atomic():
            if to_create:
                Attendance.objects.bulk_create(to_create)
            if to_update:
                Attendance.objects.bulk_update(to_update, fields=['status', 'note', 'marked_by'])

        saved = Attendance.objects.filter(group=group, date=date, student_id__in=student_ids).select_related('student', 'group', 'marked_by')
        serializer = AttendanceSerializer(saved, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
