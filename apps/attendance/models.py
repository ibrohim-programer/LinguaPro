from django.db import models
from apps.groups.models import Group
from django.contrib.auth import get_user_model
User = get_user_model()
 
class Attendance(models.Model):
    student = models.ForeignKey(User,on_delete=models.CASCADE,related_name='attendances',verbose_name="O'quvchi" , limit_choices_to={'role' :'student'})
    group = models.ForeignKey(Group,on_delete=models.CASCADE,related_name='attendances',verbose_name='Guruh')
    date = models.DateField(verbose_name='Dars sanasi')
    class AttendanceStatus(models.TextChoices):
        PRESENT = 'present', 'Keldi'     
        ABSENT  = 'absent',  'Kelmadi'   
        LATE    = 'late',    'Kech qoldi'
 
    status = models.CharField(max_length=10,choices=AttendanceStatus.choices,default=AttendanceStatus.PRESENT,verbose_name='Davomat holati')
    note = models.CharField(max_length=255,blank=True,verbose_name='Izoh')
    marked_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,verbose_name='Kim belgilagan')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('student', 'group', 'date')
        ordering = ['-date']
 
    def __str__(self):
        return f'{self.student} | {self.date} | {self.status}'