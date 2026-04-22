from django.db import models
 
class Course(models.Model):
    name = models.CharField(max_length=200, verbose_name='Kurs nomi')
    description = models.TextField(blank=True, verbose_name='Tavsif')
    class Category(models.TextChoices):
        IELTS   = 'ielts',   'IELTS'
        TOEFL   = 'toefl',   'TOEFL'
        GENERAL = 'general', 'General English'
        KIDS    = 'kids',    "Bolalar uchun"
        BUSINESS= 'business','Business English'
 
    category = models.CharField(max_length=100,verbose_name='Kategoriya')
    class Level(models.TextChoices):
        BEGINNER     = 'beginner',     'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED     = 'advanced',     'Advanced'
 
    level = models.CharField(max_length=15,choices=Level.choices,verbose_name='Daraja')
    duration_months = models.PositiveIntegerField(default=3, verbose_name='Davomiyligi (oy)')
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Narxi')
    image = models.CharField(blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return self.name
