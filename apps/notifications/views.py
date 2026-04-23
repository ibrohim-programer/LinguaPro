from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import GenericAPIView , ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema

from .models import Notification
from .serializers import SendNotificationSerializer, NotificationSerializer

User = get_user_model()

@extend_schema(tags=['Admin Send Notification'],summary="Admin --> Teacher yoki Studentlarga xabar yuboradi" )
class SendNotificationView(GenericAPIView):
    serializer_class   = SendNotificationSerializer
    permission_classes = [IsAdminUser]
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target_role = serializer.validated_data['target_role']
        title = serializer.validated_data['title']
        message = serializer.validated_data['message']
        if target_role == 'all':
            users = User.objects.filter(role__in=['teacher', 'student'])
        else:
            users = User.objects.filter(role=target_role)

        count = 0
        for user in users:
            Notification.objects.create(recipient=user,title=title,message=message,)
            count += 1

        return Response({'detail': f'{count} ta foydalanuvchiga xabar yuborildi!'},status=status.HTTP_201_CREATED)


@extend_schema(tags=['Admin Send Notification'],summary="User o'z xabarlarini ko'radi" )
class MyNotificationsView(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


@extend_schema(tags=['Admin Send Notification'],summary=" Xabarni o'qildi deb belgilash" )
class MarkAsReadView(GenericAPIView):
    serializer_class   = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def patch(self, request, pk=None):
        notification         = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'detail': 'Xabar o\'qildi deb belgilandi!'})


@extend_schema(tags=['Admin Send Notification'],summary="Barcha xabarlarni o'qildi deb belgilash" )
class MarkAllAsReadView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request):
        updated = Notification.objects.filter(recipient=request.user,is_read=False).update(is_read=True)
        return Response({'detail': f"{updated} ta xabar o'qildi deb belgilandi!"})