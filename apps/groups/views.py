from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers as rf_serializers
from drf_spectacular.utils import extend_schema, inline_serializer

from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.common.permissions import IsAdmin, IsAdminOrTeacher
from .models import Group, GroupStudent
from .serailizers import GroupSerializer, AddStudentSerializer, MyGroupSerializer , AvailableStudentsSerializer, TodayScheduleSerializer
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
        if getattr(self, 'swagger_fake_view', False):   
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

        username = serializer.validated_data['username']
        student = User.objects.get(username=username , role='student')
        obj, created = GroupStudent.objects.get_or_create(group=group, student=student)

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
        400: inline_serializer('RemoveStudentError',    fields={'detail': rf_serializers.CharField()}),})

class RemoveStudentView(GenericAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAdminOrTeacher]
    serializer_class = rf_serializers.Serializer   

    def delete(self, request, pk=None, sid=None):
        group = self.get_object()
        self.check_object_permissions(request, group)
        deleted, _ = GroupStudent.objects.filter(group=group, student_id=sid).delete()

        if not deleted:
            return Response({'detail': 'Student guruhda topilmadi!'}, status=400)
        return Response({'detail': 'Student guruhdan olib tashlandi!'}, status=200)
@extend_schema(
    tags=['Group - Admin - Teacher'],
    summary="Guruhga qo'shish uchun mavjud studentlar (guruhda yo'qlar)",
)
class AvailableStudentsView(ListAPIView):
    
    serializer_class = AvailableStudentsSerializer  
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        group_id = self.kwargs['pk']
        already_in = GroupStudent.objects.filter(group_id=group_id).values_list('student_id', flat=True)
        return User.objects.filter(role='student').exclude(id__in=already_in)
        
@extend_schema(
    tags=['Group - Admin - Teacher'],
    summary="Studentlarni Ruyxati ",
)
class StudentListView(ListAPIView):
    serializer_class = AvailableStudentsSerializer
    permission_classes = [IsAdminOrTeacher]
    def get_queryset(self):
        return User.objects.filter(role = "student")


@extend_schema(
    tags=['Group - Teacher Dashboard'],
    summary="Bugungi darslar jadvali (vaqt statuslari bilan)",
    description="""
    Teacher o'z bugungi darslarini ko'radi.
    Har bir dars uchun vaqtga qarab status qaytariladi:
    - **upcoming** (Kutilmoqda): Dars hali boshlanmagan
    - **ongoing** (Darsda): Dars ayni damda bo'layapti
    - **completed** (Tugadi): Dars o'tib ketgan
    """,
)
class TodayScheduleView(ListAPIView):
    serializer_class = TodayScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Group.objects.none()

        user = self.request.user
        now = timezone.localtime(timezone.now())
        today_weekday = str(now.weekday())  # 0=Dushanba, 6=Yakshanba

        if user.role == 'teacher':
            qs = Group.objects.filter(teacher=user)
        elif user.role == 'student':
            qs = Group.objects.filter(group_students__student=user)
        else:
            return Group.objects.none()

        # Bugun dars bor guruhlarni filtr qilamiz
        result = []
        for group in qs:
            week_days = group.week_days or []
            # week_days list bo'lib saqlangan bo'lishi kerak, masalan [0,2,4]
            if today_weekday in [str(d) for d in week_days] or today_weekday in week_days:
                result.append(group.id)

        return qs.filter(id__in=result)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['now'] = timezone.localtime(timezone.now()).time()
        return context

@extend_schema(
    tags=['Group - Teacher Dashboard'],
    summary="Berilgan sanada darslar jadvali",
    description="""
    Query param orqali sana kiritiladi: `?date=2025-05-10`

    O'sha sananing hafta kuniga qarab dars bo'ladigan guruhlar ro'yxati chiqadi.

    Statuslar:
    - Bugungi sana bo'lsa → haqiqiy vaqtga qarab (upcoming/ongoing/completed)
    - O'tgan sana bo'lsa → barcha darslar **completed**
    - Kelgusi sana bo'lsa → barcha darslar **upcoming**

    Sana kiritilmasa, bugungi sana ishlatiladi.
    """,
    parameters=[
        {
            'name': 'date',
            'in': 'query',
            'required': False,
            'description': 'Sana formati: YYYY-MM-DD (masalan: 2025-05-10)',
            'schema': {'type': 'string', 'format': 'date'},
        }
    ],
)
class ScheduleByDateView(ListAPIView):
    serializer_class = TodayScheduleSerializer
    permission_classes = [IsAuthenticated]

    def _get_target_date(self):
        import datetime
        date_str = self.request.query_params.get('date')
        if date_str:
            try:
                return datetime.date.fromisoformat(date_str)
            except ValueError:
                return timezone.localtime(timezone.now()).date()
        return timezone.localtime(timezone.now()).date()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Group.objects.none()

        user = self.request.user
        target_date = self._get_target_date()
        target_weekday = str(target_date.weekday())

        if user.role == 'teacher':
            qs = Group.objects.filter(teacher=user)
        elif user.role == 'student':
            qs = Group.objects.filter(group_students__student=user)
        else:
            return Group.objects.none()

        result = []
        for group in qs:
            week_days = group.week_days or []
            if target_weekday in [str(d) for d in week_days] or target_weekday in week_days:
                result.append(group.id)

        return qs.filter(id__in=result)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        now_local = timezone.localtime(timezone.now())
        today = now_local.date()
        target_date = self._get_target_date()

        if target_date == today:
            context['now'] = now_local.time()
            context['date_mode'] = 'today'
        elif target_date < today:
            context['date_mode'] = 'past'
        else:
            context['date_mode'] = 'future'

        return context
