from django.db import models
from apps.courses.models import Course
from django.contrib.auth import get_user_model
User = get_user_model() 
class Group(models.Model):
    name = models.CharField(max_length=100,verbose_name='Guruh nomi')
    course = models.ForeignKey(Course,on_delete=models.SET_NULL,null=True,related_name='groups',verbose_name='Kurs')
    teacher = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='groups_teacher',verbose_name='Ustoz' , limit_choices_to={'role' : 'teacher'})
    start_time = models.TimeField(verbose_name='Dars boshlanishi')
    end_time   = models.TimeField(verbose_name='Dars tugashi')
    week_days = models.JSONField(default=list,verbose_name='Hafta kunlari')
    class Status(models.TextChoices):
        ACTIVE   = 'active',   'Faol'
        INACTIVE = 'inactive', 'Faolsiz'
        FINISHED = 'finished', 'Yakunlangan'
 
    status = models.CharField(max_length=10,choices=Status.choices,default=Status.ACTIVE)
    start_date = models.DateField(verbose_name='Boshlanish sanasi')
    end_date   = models.DateField(null=True, blank=True, verbose_name='Tugash sanasi')
    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return self.name


class GroupStudent(models.Model):
    group = models.ForeignKey(Group , on_delete=models.CASCADE , related_name='group_students')
    student = models.ForeignKey(User , models.CASCADE , related_name='student_groups' , limit_choices_to={'role' : 'student'})
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('group','student')
        
    def __str__(self):
        return f"{self.student} {self.group}"
    
