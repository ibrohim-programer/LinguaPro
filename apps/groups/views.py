from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers as rf_serializers
from drf_spectacular.utils import extend_schema, inline_serializer

from django.contrib.auth import get_user_model
from apps.common.permissions import IsAdmin, IsAdminOrTeacher
from .models import Group, GroupStudent
from .serailizers import GroupSerializer, AddStudentSerializer, MyGroupSerializer

User = get_user_model()


@extend_schema(tags=['Group - Crud'], summary='Admin gruppalar ruyxatini kura oldi')
class GroupListIsAdmin(ListAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAdmin]
    serializer_class = GroupSerializer


@extend_schema(tags=['Group - Crud'], summary='Admin gruppalarni yaratadi')
class GroupCreateIsAdmin(CreateAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAdmin]
    serializer_class = GroupSerializer


@extend_schema(tags=['Group - Crud'], summary='Admin gruppalarni yangilashi va uchiradi')
class GroupUpdateDeleteIsAdmin(RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAdmin]
    serializer_class = GroupSerializer
    http_method_names = ['put', 'delete']


@extend_schema(
    tags=['Group - Admin - Teacher'],
    summary='Admin va Teacherlar uchun bulim',
    description="""
    Admin barcha guruxlar ruyxatini kura oladi
    Teacher uz guruxlarini ruyxatini kura oladi
    Student uz guruxlarini ruyxatini kura oladi
    """
)
class MyGroupsView(ListAPIView):
    serializer_class = MyGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):   # ✅ AnonymousUser xatosini oldini oladi
            return Group.objects.none()

        user = self.request.user

        if user.role == 'teacher':
            return Group.objects.filter(teacher=user)
        elif user.role == 'student':
            return Group.objects.filter(group_students__student=user)

        return Group.objects.none()


@extend_schema(
    tags=['Group - Admin - Teacher'],
    summary="Guruhga student qo'shish",
    description="""
    Admin barcha guruxlarga student qusha oladi
    Teacher uz guruxlariga student qusha oladi
    """,
    responses={
        201: inline_serializer('AddStudentResponse', fields={'detail': rf_serializers.CharField()}),
        400: inline_serializer('AddStudentError',    fields={'detail': rf_serializers.CharField()}),
    }
)
class AddStudentView(GenericAPIView):
    queryset = Group.objects.all()
    serializer_class = AddStudentSerializer
    permission_classes = [IsAdminOrTeacher]

    def post(self, request, pk=None):
        group = self.get_object()
        self.check_object_permissions(request, group)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        student_id = serializer.validated_data['student_id']
        obj, created = GroupStudent.objects.get_or_create(group=group, student_id=student_id)

        if not created:
            return Response({'detail': 'Student allaqachon guruhda!'}, status=400)

        return Response({'detail': "Student muvaffaqiyatli qo'shildi!"}, status=201)


@extend_schema(
    tags=['Group - Admin - Teacher'],
    summary="Guruhdan student o'chirish",
    description="""
    Admin barcha guruxlardagi studentlarni uchira oladi
    Teacher uz guruxlaridagi studentlarni uchira oladi
    """,
    responses={
        200: inline_serializer('RemoveStudentResponse', fields={'detail': rf_serializers.CharField()}),
        400: inline_serializer('RemoveStudentError',    fields={'detail': rf_serializers.CharField()}),
    }
)
class RemoveStudentView(GenericAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAdminOrTeacher]
    serializer_class = rf_serializers.Serializer   # ✅ spectacular uchun — request body yo'q

    def delete(self, request, pk=None, sid=None):
        group = self.get_object()
        self.check_object_permissions(request, group)

        deleted, _ = GroupStudent.objects.filter(group=group, student_id=sid).delete()

        if not deleted:
            return Response({'detail': 'Student guruhda topilmadi!'}, status=400)

        return Response({'detail': 'Student guruhdan olib tashlandi!'}, status=200)