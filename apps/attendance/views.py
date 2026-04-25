from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q

from .models import Attendance
from .serializers import AttendanceSerializer, MyAttendanceSerializer, AttendanceStatsSerializer
from apps.groups.models import Group
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import inline_serializer          # ✅ FIX import
from rest_framework import serializers as rf_serializers     # ✅ FIX import
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


@extend_schema(tags=['Attendance Crud'], summary='Admin - Teacher uchun')
class AttendanceUpdateView(generics.UpdateAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAdminOrTeacher]
    http_method_names = ['put']

    def get_queryset(self):
        return Attendance.objects.all()

    def perform_update(self, serializer):
        serializer.save(marked_by=self.request.user)


@extend_schema(tags=['Attendance Crud'], summary='Student uchun')
class MyAttendanceView(generics.ListAPIView):
    serializer_class = MyAttendanceSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):   # ✅ FIX: AnonymousUser xatosi
            return Attendance.objects.none()
        return Attendance.objects.filter(student=self.request.user).select_related('group')


@extend_schema(
    tags=['Attendance Crud'],
    summary='Admin - Teacher uchun',
    responses={200: AttendanceStatsSerializer},  # ✅ FIX: spectacular response ko'rsatildi
)
class AttendanceStatsView(APIView):
    permission_classes = [IsAdminOrTeacher]

    def get(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        qs = Attendance.objects.filter(group=group)
        total = qs.count()

        if total == 0:
            data = {
                'group_id': group.id, 'group_name': group.name,
                'total': 0, 'present': 0, 'absent': 0, 'late': 0,
                'present_pct': 0.0, 'absent_pct': 0.0, 'late_pct': 0.0,
            }
            return Response(data)

        counts = qs.aggregate(
            present=Count('id', filter=Q(status=Attendance.AttendanceStatus.PRESENT)),
            absent=Count('id',  filter=Q(status=Attendance.AttendanceStatus.ABSENT)),
            late=Count('id',    filter=Q(status=Attendance.AttendanceStatus.LATE)),
        )

        data = {
            'group_id':    group.id,
            'group_name':  group.name,
            'total':       total,
            'present':     counts['present'],
            'absent':      counts['absent'],
            'late':        counts['late'],
            'present_pct': round(counts['present'] / total * 100, 1),
            'absent_pct':  round(counts['absent']  / total * 100, 1),
            'late_pct':    round(counts['late']    / total * 100, 1),
        }
        serializer = AttendanceStatsSerializer(data)
        return Response(serializer.data)