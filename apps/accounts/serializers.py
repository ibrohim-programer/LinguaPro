from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
import re
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True,label='Parolni tasdiqlang')
    class Meta:
        model = User
        fields = ['username',"phone",'password','password2','phone','role',]
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8},}
    def validate_username(self, value):
        value = value.lower()
        if not re.match(r'^[a-z0-9_]+$', value):
            raise serializers.ValidationError("Foydalanuvchi nomida faqat lotin harflar, raqamlar va _ bo'lishi mumkin.")
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Parollar mos kelmaydi. Qayta kiriting.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(label='Foydalanuvchi nomi')
    password = serializers.CharField(write_only=True,label='Parol')

    def validate(self, data):
        username = data.get('username', '').lower()
        password = data.get('password')
        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError('Foydalanuvchi nomi yoki parol noto\'g\'ri.')

        if not user.is_active:
            raise serializers.ValidationError('Akkaunt bloklangan. Administrator bilan bog\'laning.')

        data['user'] = user
        return data

class ProfileSerealizers(serializers.ModelSerializer):
    username = serializers.CharField(read_only = True)
    class Meta:
        model = User
        fields = ["id","role","username","phone","avatar","timezone","bio","learning_goal","created_at","updated_at", ]
        read_only_fields = ['id' , 'email' , 'role' ]
        
class ProfileUpdateSerealizers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username","avatar","timezone","bio","learning_goal", ]
        read_only_fields = ['id']

    def validate_phone(self, value):
        if value:
            import re
            if not re.match(r'^\+?[0-9]{9,15}$', value):
                raise serializers.ValidationError("Telefon raqam noto'g'ri formatda. Masalan: +998901234567")
        return value
        
class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField( read_only=True)
    role_display = serializers.CharField( read_only=True)
    class Meta:
        model = User
        fields = ['id','username','full_name','role','role_display','phone','is_active','created_at',]   

class ForgotPasswordSerealizers(serializers.Serializer):
    username = serializers.CharField(write_only = True , required = True)
    phone = serializers.CharField(write_only = True , required = True)    
    def validate_username(self, value):
        try:
            if not User.objects.filter(username = value).exists():
                raise serializers.ValidationError("Ushbu username ega foydalanuvchi mavjud emas.")
            return value
        except Exception as e:
            raise serializers.ValidationError({"Xatolik yuzaga keldi" : str(e)})
        
    def create(self, validated_data):
        try:
            username = validated_data['username']
            phone = validated_data['phone']
            user = User.objects.get(username=username , phone=phone)
            return user
            
        except Exception as e:
            raise serializers.ValidationError({"Xatolik yuzaga keldi" : str(e)})
          
    
class VirfiyPasswordSerialezers(serializers.Serializer):
    username = serializers.CharField(write_only = True , required = True)  
    new_password = serializers.CharField(write_only = True , required = True)
    confirm_password = serializers.CharField(write_only = True , required = True)
    
    def validate(self, attrs):
        try:           
            if attrs['new_password'] != attrs['confirm_password']:
                raise serializers.ValidationError("Passwords to not match.")
            return attrs
        
        except Exception as e:
            raise serializers.ValidationError({"Xatolik yuzaga keldi" : str(e)})
        
        
class UserListAdminSerailizirs(serializers.Serializer):
     class Meta:
        model = User
        fields = [
            'id',
            'username',
            'full_name',
            'role',
            'role_display',
            'phone',
            'is_active',
            'created_at',
        ]