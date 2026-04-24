from django.db import models
from apps.groups.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()
 
class Assignment(models.Model):
    title = models.CharField(max_length=200, verbose_name='Vazifa nomi')
    description = models.TextField(blank=True, verbose_name='Tavsif')
    group = models.ForeignKey(Group,on_delete=models.CASCADE,related_name='assignments',verbose_name='Guruh')
    created_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='created_assignments',limit_choices_to={'role' : 'teacher'})
    deadline = models.DateTimeField(verbose_name='Topshirish muddati')
    max_score = models.PositiveIntegerField(default=100, verbose_name='Maksimal ball')
    attachment = models.FileField(upload_to='assignments/',blank=True,null=True,verbose_name='Fayl')
 
    class SubmissionType(models.TextChoices):
        TEXT = 'text', 'Matn'
        FILE = 'file', 'Fayl'
        LINK = 'link', 'Havola'
 
    submission_type = models.CharField(max_length=10,choices=SubmissionType.choices,default=SubmissionType.TEXT)
    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return self.title
 
 
class Submission(models.Model):
    assignment = models.ForeignKey(Assignment,on_delete=models.CASCADE,related_name='submissions')
    student = models.ForeignKey(User,on_delete=models.CASCADE,related_name='submissions',limit_choices_to={'role' : 'student'})
    text_answer = models.TextField(blank=True)
    file_answer = models.FileField(upload_to='submissions/', blank=True, null=True)
    score = models.PositiveIntegerField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('assignment', 'student')