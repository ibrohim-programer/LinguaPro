from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
 
class Teacher(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='teacher_profile',verbose_name='Foydalanuvchi')
    class Level(models.TextChoices):
        Beginner = 'beginner', 'Beginner'
        Elementary    = 'elementary',    'Elementary'
        Pre_Intermediate = 'pre_intermediate', 'Pre-Intermediate'
        Intermediate = 'intermediate', 'Intermediate'
        Upper_Intermediate = 'upper_Intermediate' ,'Upper-Intermediate'
        Advanced = 'advanced' ,'Advanced'
        Proficiency = 'proficiency' ,'Proficiency'
 
    level = models.CharField(max_length=30, choices=Level.choices, default=Level.Beginner ,verbose_name="Daraja")
    experience_years = models.PositiveIntegerField(default=0,verbose_name='Tajriba (yil)')
    is_active = models.BooleanField(default=True,verbose_name='Faol holati')
    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return self.user.get_full_name()