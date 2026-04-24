from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class BroadcastNotification(models.Model):

    class TargetRole(models.TextChoices):
        ALL     = 'all',     'Barchaga'
        TEACHER = 'teacher', 'O\'qituvchilar'
        STUDENT = 'student', 'O\'quvchilar'

    sender      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_broadcasts')
    title       = models.CharField(max_length=200)
    message     = models.TextField()
    target_role = models.CharField(max_length=10, choices=TargetRole.choices, default=TargetRole.ALL)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.target_role} | {self.title}'


class Notification(models.Model):

    recipient          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title              = models.CharField(max_length=200)
    message            = models.TextField()
    is_read            = models.BooleanField(default=False)
    related_object_id  = models.PositiveIntegerField(null=True, blank=True)
    broadcast          = models.ForeignKey(BroadcastNotification, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    created_at         = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.recipient.username} | {self.title}'