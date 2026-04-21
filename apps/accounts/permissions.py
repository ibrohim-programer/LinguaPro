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