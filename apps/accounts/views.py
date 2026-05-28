from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.generics import GenericAPIView, UpdateAPIView , DestroyAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model ,logout
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

from .serializers import (
    RegisterSerializer, LoginSerializer, ProfileSerealizers,
    ProfileUpdateSerealizers, VirfiyPasswordSerialezers,
    UserListSerializer, ForgotPasswordSerealizers, UserListAdminSerailizirs
)
from .permissions import IsAdmin

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


@extend_schema(
    tags=["Auth - Register - Login"],
    summary="Foydalanuvchini ro'yxatdan o'tkazish",
    description="""
    Bu endpoint quyidagi amallarni bajaradi:
    - Yangi foydalanuvchini ro'yxatdan o'tkazish

    Role :
     - student
     - teacher
     - admin
    """
)
class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        return Response({
            'message': "Ro'yxatdan muvaffaqiyatli o'tdingiz!",
            'user': ProfileSerealizers(user).data
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Auth - Register - Login"],
    summary="Tizimga kirish",
    description="""
    Bu endpoint quyidagi amallarni bajaradi:
     - Email va Passwordni kiriting.
     - Passwordni unutgan bulasangiz unutdimni bosing.
    """
)
class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)
        return Response({
            'message': f'Xush kelibsiz, {user.full_name}!',
            'user': ProfileSerealizers(user).data,
            'tokens': tokens,
        }, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Profile - Crud"],
    summary="My Profile",
    description="Barcha malumotlarningizni kurung.",
    responses={200: ProfileSerealizers}, 
)
class ProfileView(GenericAPIView):              
    serializer_class = ProfileSerealizers       
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        serializer = ProfileSerealizers(user, context={'request': request})
        return Response({"User Data": serializer.data}, status=200)


@extend_schema(
    tags=["Profile - Crud"],
    summary="My Profile - Update",
    description="Barcha malumotlarningizni yangilang.",
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'username': {
                    'type': 'string',
                    'description': 'Foydalanuvchi nomi',
                },
                'full_name': {
                    'type': 'string',
                    'description': 'To\'liq ism',
                },
                'avatar': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'Profil rasmi',
                },
                'timezone': {
                    'type': 'string',
                    'description': 'Vaqt zonasi',
                },
                'bio': {
                    'type': 'string',
                    'description': 'Qisqa ma\'lumot',
                },
                'learning_goal': {
                    'type': 'string',
                    'description': 'O\'qish maqsadi',
                },
            },
        }
    },
    responses={200: ProfileUpdateSerealizers},
)

class ProfileUpdateView(UpdateAPIView):
    serializer_class = ProfileUpdateSerealizers
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        try:
            user = self.request.user
            # request.FILES ham qabul qilish uchun
            serializer = ProfileUpdateSerealizers(
                user,
                data=request.data,
                context={'request': request},  # ← bu qo'shildi
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "message": "👤 Profil muvaffaqiyatli yangilandi ✅",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
@extend_schema(
    tags=["Profile - Crud"],
    summary="My Profile - Logout",
    description="MyProfile Logout"
)

class MyProfileLogoutView(APIView):
    def post(self,request):
        logout(request)
        return Response({'delete':'Successfully logged out.'},status=status.HTTP_200_OK)
        
@extend_schema(
    tags=["Profile - Delete"],
    summary="User delete - Admin uchun",
    description="Barcha malumotlarningizni yangilang."
)

class ProfileDelete(DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSerealizers
    permission_classes = [IsAuthenticated , IsAdmin]
    lookup_field = 'id'
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        user_id = instance.id
        
        self.perform_destroy(instance)
        return Response({"result": f"User with id {user_id} deleted successfully"},status=status.HTTP_204_NO_CONTENT)

@extend_schema(
    tags=["I forgot my password."],
    summary="Forgot - Password Amal : 1",
    description="""
    Passwordingizni unitdingizmi !
     - Username va phoneingizni kiriting.
    """
)
class ForgotPasswordView(GenericAPIView):
    serializer_class = ForgotPasswordSerealizers
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serealizers = self.serializer_class(data=request.data)
            serealizers.is_valid(raise_exception=True)
            serealizers.save()
            return Response("Success", status=201)
        except Exception as e:
            return Response({"Error": str(e)}, status=400)


@extend_schema(
    tags=["I forgot my password."],
    summary="Verfiy - Password Amal : 2",
    description="""
    Passwordingizni unitdingizmi !
     - Email
     - Username
     - new_password : Yangi parolingiz
     - confirm_password : Parolingizni takror yozing.
    """
)
class VerfiyPasswordView(GenericAPIView):
    serializer_class = VirfiyPasswordSerialezers
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serealizers = self.serializer_class(data=request.data)
            serealizers.is_valid(raise_exception=True)
            username = serealizers.validated_data['username']
            new_password = serealizers.validated_data['new_password']
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            tokens = get_tokens_for_user(user)
            return Response({
                "message": "Parol muvaffaqiyatli yangilandi ✅",
                "tokens": tokens
            }, status=200)
        except Exception as e:
            return Response({"Error": str(e)}, status=400)


@extend_schema(tags=['Admin User list full'], summary='Admin barcha userlar ruyxatini kuradi.')
class UserListAdminView(GenericAPIView):
    serializer_class = UserListAdminSerailizirs
    permission_classes = [IsAdmin]

    def get(self, request):
        users = User.objects.all()
        role = request.query_params.get('role')
        if role:
            users = users.filter(role=role)
        search = request.query_params.get('search')
        if search:
            from django.db.models import Q
            users = users.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)