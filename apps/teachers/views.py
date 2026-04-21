from rest_framework import status
from rest_framework.generics import ListAPIView , CreateAPIView , RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.db.models import Q

from apps.accounts.permissions import IsAdmin, IsTeacher
from .models import Teacher
from .serailizers import (
    TeacherCreateSerializer,
    TeacherListSerializer,
    TeacherDetailSerializer,
    TeacherUpdateSerializer,
)


@extend_schema(
    tags=['Teacher - Crud'],
    summary='Teacherlar ruyxati /'    
    )


class TeacherListView(ListAPIView):
    serializer_class = TeacherCreateSerializer
    permission_classes = [IsAdmin]
    def get(self, request):
        teachers = Teacher.objects.select_related('user').all()

        search = request.query_params.get('search')
        if search:
            teachers = teachers.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)  |
                Q(user__username__icontains=search)   |
                Q(user__phone__icontains=search)
            )

        level = request.query_params.get('level')
        if level:
            teachers = teachers.filter(level=level)

        is_active = request.query_params.get('is_active')
        if is_active is not None:
            teachers = teachers.filter(is_active=is_active.lower() == 'true')

        serializer = TeacherListSerializer(teachers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(
    tags=['Teacher - Crud'],
    summary='Teacher yaratish bulimi /'    
    )
class TeacherCreateView(CreateAPIView):
    serializer_class = TeacherCreateSerializer
    permission_classes = [IsAdmin]
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsAdmin()]

    def get(self, request):
        teachers = Teacher.objects.select_related('user').all()

        search = request.query_params.get('search')
        if search:
            teachers = teachers.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)  |
                Q(user__username__icontains=search)   |
                Q(user__phone__icontains=search)
            )

        level = request.query_params.get('level')
        if level:
            teachers = teachers.filter(level=level)

        is_active = request.query_params.get('is_active')
        if is_active is not None:
            teachers = teachers.filter(is_active=is_active.lower() == 'true')

        serializer = TeacherListSerializer(teachers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TeacherCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        teacher = serializer.save()
        return Response(
            TeacherDetailSerializer(teacher).data,
            status=status.HTTP_201_CREATED
        )

@extend_schema(
    tags=['Teacher - Crud'],
    summary='Teacherni Update - Delete qulish bulimi /'    
    )

class TeacherDetailUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]

    def get_object(self, pk):
        try:
            return Teacher.objects.select_related('user').get(pk=pk)
        except Teacher.DoesNotExist:
            return None

    def get(self, request, pk):
        teacher = self.get_object(pk)
        if not teacher:
            return Response({'error': 'Topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TeacherDetailSerializer(teacher)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        teacher = self.get_object(pk)
        if not teacher:
            return Response({'error': 'Topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TeacherUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        updated = serializer.update(teacher, serializer.validated_data)
        return Response(TeacherDetailSerializer(updated).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        teacher = self.get_object(pk)
        if not teacher:
            return Response({'error': 'Topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        user = teacher.user
        teacher.delete()
        user.delete()
        return Response({'message': "O'qituvchi o'chirildi."}, status=status.HTTP_200_OK)


class TeacherDashboardView(ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_teacher:
            return Response({'error': 'Ruxsat yoq.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            return Response({'error': 'O\'qituvchi profili topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        groups  = teacher.groups.filter(status='active')
        students = set()
        for group in groups:
            for s in group.students.all():
                students.add(s.id)

        data = {
            'full_name'       : request.user.full_name,
            'level'           : teacher.get_level_display(),
            'experience_years': teacher.experience_years,
            'total_groups'    : groups.count(),
            'total_students'  : len(students),
        }
        return Response(data, status=status.HTTP_200_OK)