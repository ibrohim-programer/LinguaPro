from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
class Notification(models.Model):
    class TargetRole(models.TextChoices):
        TEACHER = 'teacher', 'Ustoz'
        STUDENT = 'student', "O'quvchi"
        ALL = 'all', 'Hammaga'

    recipient = models.ForeignKey(User, on_delete=models.CASCADE,related_name='notifications',verbose_name='Qabul qiluvchi')
    title = models.CharField(max_length=200, verbose_name='Sarlavha')
    message = models.TextField(verbose_name='Matn')
    is_read = models.BooleanField(default=False, verbose_name="O'qildi")
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.recipient.username} | {self.title}'