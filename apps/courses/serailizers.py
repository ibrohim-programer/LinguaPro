from rest_framework import serializers
from .models import Course

class CourseSerializer(serializers.ModelSerializer):

    category_display = serializers.CharField(source='get_category_display',read_only=True)
    level_display = serializers.CharField(source='get_level_display',read_only=True)

    class Meta:
        model = Course
        fields = ['id','name','description','category','category_display','level','level_display','duration_months','price','image','is_active','created_at',]
        
        read_only_fields = ['id','created_at','category_display','level_display',]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Kurs nomi kamida 3 ta harfdan iborat bo‘lishi kerak.")
        return value

    def validate_duration_months(self, value):
        if value <= 0:
            raise serializers.ValidationError("Davomiylik 0 dan katta bo‘lishi kerak.")
        return value
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Narx 0 dan katta bo‘lishi kerak.")
        return value
