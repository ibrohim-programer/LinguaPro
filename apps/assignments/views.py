import os
import uuid

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from django.utils import timezone

from drf_spectacular.utils import extend_schema, OpenApiTypes
from drf_spectacular.openapi import AutoSchema
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsAdminOrTeacher, IsStudent
from .models import Assignment, Submission
from .serailizers import (
    AssignmentSerializer,
    FileUploadResponseSerializer,
    FileUploadSerializer,
    GradeSubmissionSerializer,
    StudentSubmissionStatusSerializer,
    SubmissionSerializer,
)

User = get_user_model()


def deactivate_expired_assignments():
    Assignment.objects.filter(
        deadline__lt=timezone.now(), is_active=True
    ).update(is_active=False)


# ─────────────────────────────────────────────
#  O'ZGARMAGAN
# ─────────────────────────────────────────────
@extend_schema(
    tags=['Assignment Crud'],
    summary='Admin va Teacher uchun uyga vazifa yaratish va kurish bulimi',
)
class AssignmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Assignment.objects.none()
        deactivate_expired_assignments()
        user = self.request.user
        if user.role == 'admin':
            return Assignment.objects.all().order_by('-created_at')
        return Assignment.objects.filter(created_by=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


@extend_schema(tags=['Assignment Crud'], summary="Vazifa tafsilot / tahrirlash / o'chirish")
class AssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssignmentSerializer
    http_method_names = ['get', 'put', 'delete']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [IsAdminOrTeacher()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Assignment.objects.none()
        deactivate_expired_assignments()
        user = self.request.user
        if user.role == 'admin':
            return Assignment.objects.all().order_by('-created_at')
        return Assignment.objects.filter(created_by=user).order_by('-created_at')


@extend_schema(tags=['Assignment Crud'], summary="Student o'z vazifalarini ko'radi")
class MyAssignmentsView(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Assignment.objects.none()
        deactivate_expired_assignments()
        user = self.request.user
        student_group_ids = user.student_groups.values_list('group_id', flat=True)
        return Assignment.objects.filter(
            group_id__in=student_group_ids
        ).order_by('-created_at')


# ─────────────────────────────────────────────
#  YANGI: Fayl yuklash endpointi
#  POST /assignments/upload/
# ─────────────────────────────────────────────
@extend_schema(
    tags=['Assignment Crud'],
    summary='Fayl yuklash (oldindan yuklash)',
    description="""
Fayl yuklash uchun alohida endpoint.

**Ish tartibi:**
1. `POST /assignments/upload/` → `file_path` va `file_url` oling
2. `POST /assignments/{pk}/submit/` → `file_path` ni body ga yuboring

Bu orqali faylni submit dan oldin yuklash va URL ni ko'rish mumkin.
    """,
    # ✅ format: binary → Swaggerda "Choose File" tugmasi chiqadi
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'file': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'Yuklanadigan fayl (max 50MB)',
                }
            },
            'required': ['file'],
        }
    },
    responses={201: FileUploadResponseSerializer},
)
class AssignmentFileUploadView(APIView):
    """
    POST /assignments/upload/
    Multipart fayl qabul qiladi, saqlaydi va URL qaytaradi.
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsStudent]

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data['file']

        # Unique nom — bir xil nomli fayllar ustiga yozilmasin
        ext = os.path.splitext(file.name)[1].lower()
        unique_filename = f'submissions/uploads/{uuid.uuid4().hex}{ext}'

        # Faylni saqlash
        saved_path = default_storage.save(
            unique_filename,
            ContentFile(file.read()),
        )

        # To'liq URL
        file_url = request.build_absolute_uri(default_storage.url(saved_path))

        response_data = {
            'file_path': saved_path,   # submit da shu qiymatni yuboring
            'file_url':  file_url,     # faylni ko'rish uchun
            'file_name': file.name,
            'file_size': file.size,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


# ─────────────────────────────────────────────
#  O'ZGARGAN: file_path orqali ham submit qilish
#  POST /assignments/{pk}/submit/
# ─────────────────────────────────────────────
@extend_schema(
    tags=['Assignment Crud'],
    summary='Student vazifa topshiradi',
    description="""
Fayl bilan topshirish uchun ikki yo'l:

**1-yo'l (to'g'ridan-to'g'ri):** `file_answer` maydoniga fayl tanlang.

**2-yo'l (oldindan yuklash):**
Avval `POST /assignments/upload/` ga fayl yuboring → `file_path` oling →
keyin shu `file_path` ni submit da body ga yuboring (`file_answer` bo'sh qoladi).
    """,
    # ✅ file_answer → format:binary → Swaggerda "Choose File" tugmasi chiqadi
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'assignment': {
                    'type': 'integer',
                    'description': 'Vazifa ID si',
                },
                'text_answer': {
                    'type': 'string',
                    'description': 'Matnli javob (ixtiyoriy)',
                },
                'file_answer': {
                    'type': 'string',
                    'format': 'binary',          
                    'description': 'Fayl yuklab topshirish (ixtiyoriy)',
                },
                'file_path': {
                    'type': 'string',
                    'description': '/upload/ dan olingan file_path (file_answer o\'rniga)',
                },
            },
            'required': ['assignment'],
        }
    },
    responses={201: SubmissionSerializer},
)
class SubmitAssignmentView(generics.GenericAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [IsStudent]

    def post(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk)
        student = request.user

        if not assignment.is_active:
            return Response(
                {'detail': "Vazifaning muddati tugagan, topshirib bo'lmaydi."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Submission.objects.filter(assignment=assignment, student=student).exists():
            return Response(
                {'detail': 'Siz bu vazifani allaqachon topshirgansiz.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # file_path: oldindan yuklangan faylning yo'li (upload endpointdan olingan)
        file_path = request.data.get('file_path')

        serializer = SubmissionSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(assignment=assignment, student=student)

        # Agar file_path berilgan bo'lsa va fayl yuklanmagan bo'lsa —
        # oldindan yuklangan faylni bog'laymiz
        if file_path and not instance.file_answer:
            if default_storage.exists(file_path):
                instance.file_answer.name = file_path
                instance.save(update_fields=['file_answer'])
            else:
                instance.delete()
                return Response(
                    {'detail': 'file_path topilmadi. Avval /upload/ ga yuboring.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            SubmissionSerializer(instance, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


# ─────────────────────────────────────────────
#  O'ZGARMAGAN
# ─────────────────────────────────────────────
@extend_schema(tags=['Assignment Crud'], summary='Teacher ball beradi')
class GradeSubmissionView(generics.UpdateAPIView):
    queryset = Submission.objects.all()
    serializer_class = GradeSubmissionSerializer
    permission_classes = [IsAdminOrTeacher]
    http_method_names = ['put']


# ─────────────────────────────────────────────
#  O'ZGARGAN: file_answer → file_url (bug fix)
# ─────────────────────────────────────────────
@extend_schema(
    tags=['Assignment Crud'],
    summary="Vazifani topshirgan va topshirmagan o'quvchilar ro'yxati",
)
class AssignmentSubmissionStatusView(generics.GenericAPIView):
    permission_classes = [IsAdminOrTeacher]
    serializer_class = StudentSubmissionStatusSerializer

    def get(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk)
        group = assignment.group
        group_students = group.group_students.select_related('student').all()

        submissions = Submission.objects.filter(
            assignment=assignment
        ).select_related('student')
        submission_map = {sub.student_id: sub for sub in submissions}

        result = []
        for gs in group_students:
            student = gs.student
            submission = submission_map.get(student.id)

            # BUG FIX: absolute URL qaytaradi (avval null kelardi)
            if submission and submission.file_answer:
                file_url = request.build_absolute_uri(submission.file_answer.url)
            else:
                file_url = None

            result.append({
                'student_id':   student.id,
                'username':     student.username,
                'full_name':    getattr(student, 'full_name', '') or student.get_full_name(),
                'status':       'topshirgan' if submission else 'topshirmagan',
                'submitted_at': submission.submitted_at if submission else None,
                'score':        submission.score if submission else None,
                'text_answer':  submission.text_answer if submission else None,
                'file_url':     file_url,
            })

        serializer = self.get_serializer(result, many=True)
        return Response(serializer.data)