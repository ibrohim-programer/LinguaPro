from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Assignment, Submission
from .serailizers import AssignmentSerializer, SubmissionSerializer, GradeSubmissionSerializer
from apps.common.permissions import IsAdminOrTeacher, IsStudent, IsTeacher, IsAdmin
from drf_spectacular.utils import extend_schema
from django.utils import timezone
User = get_user_model()


def deactivate_expired_assignments():
    Assignment.objects.filter(deadline__lt = timezone.now(), is_active=True).update(is_active=False)


@extend_schema(tags=['Assignment Crud'], summary='Admin va Teacher uchun uyga vazifa yaratish va kurish bulimi')
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


@extend_schema(
    tags=['Assignment Crud'],
    summary='Admin va Teacher uchun uyga vazifa yaratish va uchurish bulimi',
    description='''
     — tafsilotlar (hammasi)
     — tahrirlash (Teacher)
     — o\'chirish (Teacher/Admin)
    '''
)
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
        if user.role == "admin":
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
        return Assignment.objects.filter(group_id__in=student_group_ids).order_by('-created_at')


@extend_schema(tags=['Assignment Crud'], summary='Student vazifa topshiradi')
class SubmitAssignmentView(generics.GenericAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [IsStudent]

    def post(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk)
        student = get_object_or_404(User, id=request.user.id)


        if not assignment.is_active:
             return Response(
                {'detail': 'Vazifaning muddati tugagan, topshirib bo\'lmaydi.'},
                status=status.HTTP_400_BAD_REQUEST
            )


        if Submission.objects.filter(assignment=assignment, student=student).exists():
            return Response(
                {'detail': 'Siz bu vazifani allaqachon topshirgansiz.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(assignment=assignment, student=student)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Assignment Crud'], summary='Teacher ball beradi')
class GradeSubmissionView(generics.UpdateAPIView):
    queryset = Submission.objects.all()
    serializer_class = GradeSubmissionSerializer
    permission_classes = [IsAdminOrTeacher]
    http_method_names = ['put']