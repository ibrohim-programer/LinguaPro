# from django.db import models
# from django.contrib.auth import get_user_model

# User = get_user_model()


# class Result(models.Model):
#     ROLE_CHOICES = (
#         ("teacher", "Teacher"),
#         ("student", "Student"),
#     )

#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="results",
#         verbose_name="Foydalanuvchi",
#     )
#     role = models.CharField(
#         max_length=20,
#         choices=ROLE_CHOICES,
#         editable=False,
#         verbose_name="Rol",
#     )
#     score = models.FloatField(verbose_name="Ball")
#     subject = models.CharField(max_length=255, verbose_name="Fan/Mavzu")
#     description = models.TextField(blank=True, null=True, verbose_name="Izoh")
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = "results"
#         verbose_name = "Natija"
#         verbose_name_plural = "Natijalar"
#         ordering = ["-created_at"]

#     def save(self, *args, **kwargs):
#         # Userning roliga qarab avtomatik role o'rnatiladi
#         if hasattr(self.user, "role"):
#             self.role = self.user.role  # User modelida role field bo'lsa
#         elif self.user.groups.filter(name="teacher").exists():
#             self.role = "teacher"
#         elif self.user.groups.filter(name="student").exists():
#             self.role = "student"
#         else:
#             # Default: is_staff bo'lsa teacher, aks holda student
#             self.role = "teacher" if self.user.is_staff else "student"
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.user.username} | {self.role} | {self.subject} — {self.score}"