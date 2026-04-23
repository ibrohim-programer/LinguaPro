from django.shortcuts import render
from rest_framework.generics import ListAPIView,CreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from apps.common.permissions import *
from .models import Course
from .serailizers import CourseSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["Course"],summary='Kurslar ruyxati Admin uchun .')  
class CourseListView(ListAPIView):
    queryset = Course.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly , IsAdmin]
    serializer_class = CourseSerializer

@extend_schema(tags=["Course"], summary='Kurs yaratish bulimi Admin uchun')  
class CourseCreateView(CreateAPIView):
    queryset = Course.objects.all()
    permission_classes = [IsAdmin]
    serializer_class = CourseSerializer

@extend_schema(tags=["Course"],summary='Kurslarni yangilash va uchirish bulimi Admin uchun')  
class CourseUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    permission_classes = [IsAdmin]
    serializer_class = CourseSerializer
    http_method_names = ['put' , 'delete']
