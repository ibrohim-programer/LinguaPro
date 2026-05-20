# from rest_framework import status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.generics import get_object_or_404
# from drf_spectacular.utils import extend_schema, OpenApiResponse

# from .models import Result
# from .serializers import ResultSerializer, ResultCreateSerializer, ResultUpdateSerializer
# from apps.common.permissions import IsAdmin


# class TeacherResultListView(APIView):
#     permission_classes = [IsAdmin]

#     @extend_schema(
#         tags=["Results"],
#         summary="Teacher natijalar ro'yxati",
#         description="Barcha teacher (o'qituvchi) rolga ega foydalanuvchilarning natijalarini qaytaradi. Faqat Admin uchun ruxsat mavjud.",
#         responses={
#             200: OpenApiResponse(
#                 response=ResultSerializer(many=True),
#                 description="Teacher natijalari ro'yxati muvaffaqiyatli qaytarildi.",
#             ),
#             403: OpenApiResponse(description="Ruxsat yo'q. Faqat adminlar uchun."),
#         },
#     )
#     def get(self, request):
#         results = Result.objects.filter(role="teacher").select_related("user")
#         serializer = ResultSerializer(results, many=True)
#         return Response(
#             {
#                 "count": results.count(),
#                 "role": "teacher",
#                 "results": serializer.data,
#             },
#             status=status.HTTP_200_OK,
#         )


# class StudentResultListView(APIView):
#     permission_classes = [IsAdmin]

#     @extend_schema(
#         tags=["Results"],
#         summary="Student natijalar ro'yxati",
#         description="Barcha student (talaba) rolga ega foydalanuvchilarning natijalarini qaytaradi. Faqat Admin uchun ruxsat mavjud.",
#         responses={
#             200: OpenApiResponse(
#                 response=ResultSerializer(many=True),
#                 description="Student natijalari ro'yxati muvaffaqiyatli qaytarildi.",
#             ),
#             403: OpenApiResponse(description="Ruxsat yo'q. Faqat adminlar uchun."),
#         },
#     )
#     def get(self, request):
#         results = Result.objects.filter(role="student").select_related("user")
#         serializer = ResultSerializer(results, many=True)
#         return Response(
#             {
#                 "count": results.count(),
#                 "role": "student",
#                 "results": serializer.data,
#             },
#             status=status.HTTP_200_OK,
#         )


# class ResultCreateView(APIView):
#     permission_classes = [IsAdmin]

#     @extend_schema(
#         tags=["Results"],
#         summary="Yangi natija yaratish",
#         description=(
#             "Yangi natija yaratadi. Foydalanuvchi tanlanganida uning roli (teacher yoki student) "
#             "avtomatik aniqlanadi va shunga qarab 'role' field to'ldiriladi. Faqat Admin uchun ruxsat mavjud."
#         ),
#         request=ResultCreateSerializer,
#         responses={
#             201: OpenApiResponse(
#                 response=ResultSerializer,
#                 description="Natija muvaffaqiyatli yaratildi.",
#             ),
#             400: OpenApiResponse(description="Ma'lumotlar noto'g'ri. Validatsiya xatosi."),
#             403: OpenApiResponse(description="Ruxsat yo'q. Faqat adminlar uchun."),
#         },
#     )
#     def post(self, request):
#         serializer = ResultCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             result = serializer.save()
#             response_serializer = ResultSerializer(result)
#             return Response(
#                 {
#                     "message": "Natija muvaffaqiyatli yaratildi.",
#                     "role": result.role,
#                     "result": response_serializer.data,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class ResultUpdateDeleteView(APIView):
#     permission_classes = [IsAdmin]

#     def get_object(self, pk):
#         return get_object_or_404(Result, pk=pk)

#     @extend_schema(
#         tags=["Results"],
#         summary="Natijani to'liq yangilash (PUT)",
#         description="Berilgan id bo'yicha natijani to'liq yangilaydi. Barcha fieldlar majburiy. Faqat Admin uchun ruxsat mavjud.",
#         request=ResultUpdateSerializer,
#         responses={
#             200: OpenApiResponse(
#                 response=ResultSerializer,
#                 description="Natija muvaffaqiyatli yangilandi.",
#             ),
#             400: OpenApiResponse(description="Ma'lumotlar noto'g'ri. Validatsiya xatosi."),
#             403: OpenApiResponse(description="Ruxsat yo'q. Faqat adminlar uchun."),
#             404: OpenApiResponse(description="Natija topilmadi."),
#         },
#     )
#     def put(self, request, pk):
#         result = self.get_object(pk)
#         serializer = ResultUpdateSerializer(result, data=request.data)
#         if serializer.is_valid():
#             updated_result = serializer.save()
#             response_serializer = ResultSerializer(updated_result)
#             return Response(
#                 {
#                     "message": "Natija muvaffaqiyatli yangilandi.",
#                     "result": response_serializer.data,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     @extend_schema(
#         tags=["Results"],
#         summary="Natijani qisman yangilash (PATCH)",
#         description="Berilgan id bo'yicha natijani qisman yangilaydi. Faqat o'zgartiriladigan fieldlarni yuborish kifoya. Faqat Admin uchun ruxsat mavjud.",
#         request=ResultUpdateSerializer,
#         responses={
#             200: OpenApiResponse(
#                 response=ResultSerializer,
#                 description="Natija qisman muvaffaqiyatli yangilandi.",
#             ),
#             400: OpenApiResponse(description="Ma'lumotlar noto'g'ri. Validatsiya xatosi."),
#             403: OpenApiResponse(description="Ruxsat yo'q. Faqat adminlar uchun."),
#             404: OpenApiResponse(description="Natija topilmadi."),
#         },
#     )
#     def patch(self, request, pk):
#         result = self.get_object(pk)
#         serializer = ResultUpdateSerializer(result, data=request.data, partial=True)
#         if serializer.is_valid():
#             updated_result = serializer.save()
#             response_serializer = ResultSerializer(updated_result)
#             return Response(
#                 {
#                     "message": "Natija qisman yangilandi.",
#                     "result": response_serializer.data,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     @extend_schema(
#         tags=["Results"],
#         summary="Natijani o'chirish (DELETE)",
#         description="Berilgan id bo'yicha natijani o'chiradi. Bu amalni qaytarib bo'lmaydi. Faqat Admin uchun ruxsat mavjud.",
#         responses={
#             204: OpenApiResponse(description="Natija muvaffaqiyatli o'chirildi."),
#             403: OpenApiResponse(description="Ruxsat yo'q. Faqat adminlar uchun."),
#             404: OpenApiResponse(description="Natija topilmadi."),
#         },
#     )
#     def delete(self, request, pk):
#         result = self.get_object(pk)
#         result_id = result.id
#         result.delete()
#         return Response(
#             {"message": f"Natija (id={result_id}) muvaffaqiyatli o'chirildi."},
#             status=status.HTTP_204_NO_CONTENT,
#         )