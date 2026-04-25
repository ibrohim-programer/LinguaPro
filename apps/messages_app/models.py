from django.db import models
from django.contrib.auth import get_user_model
from apps.groups.models import Group

User = get_user_model()


def message_file_upload_path(instance, filename):
    return f'group_messages/{instance.group_id}/files/{filename}'


def message_image_upload_path(instance, filename):
    return f'group_messages/{instance.group_id}/images/{filename}'


class GroupMessage(models.Model):
    class MessageType(models.TextChoices):
        TEXT  = 'text',  'Matn'
        FILE  = 'file',  'Fayl'
        IMAGE = 'image', 'Rasm'

    group   = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Guruh'
    )
    sender  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_group_messages',
        verbose_name='Yuboruvchi'
    )
    content      = models.TextField(blank=True, null=True, verbose_name='Xabar matni')
    attachment   = models.FileField(
        upload_to=message_file_upload_path,
        blank=True, null=True,
        verbose_name='Fayl'
    )
    image        = models.ImageField(
        upload_to=message_image_upload_path,
        blank=True, null=True,
        verbose_name='Rasm'
    )
    message_type = models.CharField(
        max_length=10,
        choices=MessageType.choices,
        default=MessageType.TEXT,
        verbose_name='Xabar turi'
    )
    # Kim o'qidi
    read_by = models.ManyToManyField(
        User,
        related_name='read_group_messages',
        blank=True,
        verbose_name='O\'qiganlar'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name        = 'Guruh xabari'
        verbose_name_plural = 'Guruh xabarlari'

    def __str__(self):
        return f'{self.sender.username} → [{self.group.name}]: {self.content[:40] if self.content else self.message_type}'

    def is_read_by_user(self, user):
        return self.read_by.filter(pk=user.pk).exists()