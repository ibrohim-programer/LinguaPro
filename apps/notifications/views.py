from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Notification, BroadcastNotification
from .serializers import (
    BroadcastCreateSerializer,
    BroadcastListSerializer,
    MyNotificationSerializer,
)
from apps.common.permissions import IsAdmin 
from .services import send_broadcast
from drf_spectacular.utils import extend_schema


@extend_schema(
    operation_id='notification_broadcast_create', 
    tags=['Notification Crud'],
    summary="Admin barcha foydalanuvchilarga xabar yuborish",
    description="""
    Admin tomonidan barcha foydalanuvchilar (yoki guruhlar) uchun umumiy xabarnoma yaratiladi va yuboriladi.
    """
)
class BroadcastCreateView(generics.CreateAPIView):
    serializer_class = BroadcastCreateSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        broadcast = serializer.save(sender=self.request.user)
        send_broadcast(broadcast)


@extend_schema(
    operation_id='notification_broadcast_list',
    tags=['Notification Crud'],
    summary="Admin yuborgan umumiy xabarnomalar ruyxati",
    description="""Admin yuborgan barcha umumiy xabarnomalar ro'yxatini ko'rishi mumkin."""
)
class BroadcastListView(generics.ListAPIView):
    serializer_class = BroadcastListSerializer
    permission_classes = [IsAdmin]
    queryset = BroadcastNotification.objects.select_related('sender').prefetch_related('notifications')


@extend_schema(
    operation_id='my_notifications_list',
    tags=['Notification Crud'],
    summary="Teacher va Studentlarni xabarnomalarim ro'yxati",
    description="Tizimga kirgan foydalanuvchi o'ziga kelgan xabarlarni ko'radi. `is_read=true/false` parametri orqali filtrlash mumkin."
)
class MyNotificationListView(generics.ListAPIView):
    serializer_class = MyNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(recipient=self.request.user)
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            qs = qs.filter(is_read=is_read.lower() == 'true')
        return qs


@extend_schema(
    operation_id='notification_mark_read',
    tags=['Notification Crud'],
    summary="Xabarni o'qilgan deb belgilash Teacher va Student",
    description="Muayyan ID ga ega bo'lgan xabarnomani 'o'qilgan' holatiga o'tkazish."
)
class MarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        updated = Notification.objects.filter(pk=pk, recipient=request.user).update(is_read=True)
        if not updated:
            return Response({'detail': 'Topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'detail': 'O\'qildi.'})


@extend_schema(
    operation_id='notification_mark_all_read',
    tags=['Notification Crud'],
    summary="Barcha xabarlarni o'qilgan deb belgilash . Teacher va Student",
    description="Foydalanuvchining barcha o'qilmagan xabarlarini bittada 'o'qilgan' holatiga o'tkazadi."
)
class MarkAllReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'updated': count})


@extend_schema(
    operation_id='notification_unread_count',
    tags=['Notification Crud'],
    summary="O'qilmagan xabarlar soni : Teacher va Student",
    description="Foydalanuvchiga kelgan, lekin hali o'qilmagan xabarlarning umumiy sonini qaytaradi."
)
class UnreadCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'unread_count': count})