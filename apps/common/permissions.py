from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    message = "Bu sahifaga faqat adminlar kira oladi."
    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.is_admin)


class IsTeacher(BasePermission):
    message = "Bu sahifaga faqat o'qituvchilar kira oladi."
    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.is_teacher)


class IsStudent(BasePermission):
    message = "Bu sahifaga faqat o'quvchilar kira oladi."
    def has_permission(self, request, view):
        return ( request.user.is_authenticated and request.user.is_student )


class IsAdminOrTeacher(BasePermission):
    message = "Bu sahifaga faqat admin yoki o'qituvchilar kira oladi."
    def has_permission(self, request, view):
        return (request.user.is_authenticated and (request.user.is_admin or request.user.is_teacher))
    
    
    
class IsTeacherOfGroup(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'admin' or obj.teacher == request.user
    
from apps.groups.models import GroupStudent


def is_group_member(user, group):
    if not user or not user.is_authenticated:
        return False

    if getattr(user, 'role', None) == 'admin' or user.is_staff:
        return True

    if getattr(user, 'role', None) == 'teacher':
        return group.teacher_id == user.pk

    if getattr(user, 'role', None) == 'student':
        return GroupStudent.objects.filter(group=group, student=user).exists()

    return False


class IsGroupMember(BasePermission):
    message = "Siz bu guruhning a'zosi emassiz!"
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return is_group_member(request.user, obj)