from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN   = 'admin',   'Administrator'
        TEACHER = 'teacher', "O'qituvchi"
        STUDENT = 'student', "O'quvchi"

    role = models.CharField(max_length=10, default=Role.STUDENT , choices=Role.choices,verbose_name='Rol')
    username = models.CharField(max_length=50, unique=True, verbose_name='Foydalanuvchi nomi', error_messages={'unique': "Bu foydalanuvchi nomi band. Boshqa nom tanlang.",})
    phone = models.CharField(max_length=9,blank=True,null=True,verbose_name='Telefon raqami')
    avatar = models.URLField(blank=True,null=True,verbose_name='Profil rasmi')
    timezone = models.CharField(max_length=50,default='Asia/Tashkent',verbose_name='Vaqt zonasi')
    bio = models.TextField(blank=True,default='',verbose_name="Qisqa ma'lumot")
    learning_goal = models.TextField(blank=True,default='',verbose_name="O'qish maqsadi")
    created_at = models.DateTimeField(auto_now_add=True,verbose_name='Yaratilgan vaqt')
    updated_at = models.DateTimeField(auto_now=True,verbose_name='Yangilangan vaqt')

    EMAIL_FIELD = None
    REQUIRED_FIELDS = [] 
    
    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'
        ordering = ['-created_at'] 

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

    
    @property
    def full_name(self):
        name = f'{self.first_name} {self.last_name}'.strip()
        return name if name else self.username

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT