from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_superuser(apps, schema_editor):
    CustomUser = apps.get_model('accounts', 'CustomUser')
    password = 'ibrohim_0919'

    for username in ['Ibrohim99', 'ibrohim99']:
        user, _ = CustomUser.objects.get_or_create(
            username=username,
            defaults={
                'full_name': 'Ibrohim',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'role': 'admin',
            }
        )
        user.password = make_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.role = 'admin'
        user.save()


def reverse_superuser(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_customuser_avatar'),
    ]

    operations = [
        migrations.RunPython(create_superuser, reverse_superuser),
    ]
