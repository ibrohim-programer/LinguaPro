# from rest_framework import serializers
# from .models import Result


# class ResultSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(source="user.username", read_only=True)
#     full_name = serializers.SerializerMethodField()

#     class Meta:
#         model = Result
#         fields = [
#             "id",
#             "user",
#             "username",
#             "full_name",
#             "role",        # read-only, avtomatik to'ldiriladi
#             "subject",
#             "score",
#             "description",
#             "created_at",
#             "updated_at",
#         ]
#         read_only_fields = ["id", "role", "created_at", "updated_at"]

#     def get_full_name(self, obj):
#         return obj.user.get_full_name() or obj.user.username


# class ResultCreateSerializer(serializers.ModelSerializer):
#     """POST uchun — faqat kerakli fieldlar"""

#     class Meta:
#         model = Result
#         fields = ["id", "user", "subject", "score", "description"]
#         read_only_fields = ["id"]

#     def validate_score(self, value):
#         if value < 0 or value > 100:
#             raise serializers.ValidationError(
#                 "Ball 0 dan 100 gacha bo'lishi kerak."
#             )
#         return value


# class ResultUpdateSerializer(serializers.ModelSerializer):
#     """PUT/PATCH uchun"""

#     class Meta:
#         model = Result
#         fields = ["subject", "score", "description"]

#     def validate_score(self, value):
#         if value < 0 or value > 100:
#             raise serializers.ValidationError(
#                 "Ball 0 dan 100 gacha bo'lishi kerak."
#             )
#         return value