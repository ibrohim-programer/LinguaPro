from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers as rf_serializers      # ✅ FIX import

from .models import Notification, BroadcastNotification
from .serializers import (
    BroadcastCreateSerializer,
    BroadcastListSerializer,
    MyNotificationSerializer,
)
from apps.common.permissions import IsAdmin
from .services import send_broadcast
from drf_spectacular.utils import extend_schema, inline_serializer  # ✅ FIX import


@extend_schema(
    # ✅ FIX: operation_id olib tashlandi — GenericAPIView da kerak emas, xato chiqaradi
    tags=['Notification Crud'],
    summary="Admin barcha foydalanuvchilarga xabar yuborish",
    description="Admin tomonidan barcha foydalanuvchilar uchun umumiy xabarnoma yaratiladi."
)
class BroadcastCreateView(generics.CreateAPIView):
    serializer_class = BroadcastCreateSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        broadcast = serializer.save(sender=self.request.user)
        send_broadcast(broadcast)


@extend_schema(
    # ✅ FIX: operation_id olib tashlandi
    tags=['Notification Crud'],
    summary="Admin yuborgan umumiy xabarnomalar ruyxati",
    description="Admin yuborgan barcha umumiy xabarnomalar ro'yxatini ko'rishi mumkin."
)
class BroadcastListView(generics.ListAPIView):
    serializer_class = BroadcastListSerializer
    permission_classes = [IsAdmin]
    queryset = BroadcastNotification.objects.select_related('sender').prefetch_related('notifications')


@extend_schema(
    # ✅ FIX: operation_id olib tashlandi
    tags=['Notification Crud'],
    summary="Teacher va Studentlarni xabarnomalarim ro'yxati",
    description="Tizimga kirgan foydalanuvchi o'ziga kelgan xabarlarni ko'radi."
)
class MyNotificationListView(generics.ListAPIView):
    serializer_class = MyNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):   # ✅ FIX: AnonymousUser xatosi
            return Notification.objects.none()
        qs = Notification.objects.filter(recipient=self.request.user)
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            qs = qs.filter(is_read=is_read.lower() == 'true')
        return qs


@extend_schema(
    # ✅ FIX: operation_id olib tashlandi + responses qo'shildi
    tags=['Notification Crud'],
    summary="Xabarni o'qilgan deb belgilash",
    responses={
        200: inline_serializer('MarkReadOk',       fields={'detail': rf_serializers.CharField()}),
        404: inline_serializer('MarkReadNotFound', fields={'detail': rf_serializers.CharField()}),
    }
)
class MarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        updated = Notification.objects.filter(pk=pk, recipient=request.user).update(is_read=True)
        if not updated:
            return Response({'detail': 'Topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'detail': 'O\'qildi.'})


@extend_schema(
    # ✅ FIX: operation_id olib tashlandi + responses qo'shildi
    tags=['Notification Crud'],
    summary="Barcha xabarlarni o'qilgan deb belgilash",
    responses={
        200: inline_serializer('MarkAllReadOk', fields={'updated': rf_serializers.IntegerField()}),
    }
)
class MarkAllReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'updated': count})


@extend_schema(
    # ✅ FIX: operation_id olib tashlandi + responses qo'shildi
    tags=['Notification Crud'],
    summary="O'qilmagan xabarlar soni",
    responses={
        200: inline_serializer('NotifUnreadCount', fields={'unread_count': rf_serializers.IntegerField()}),
    }
)
class UnreadCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'unread_count': count})