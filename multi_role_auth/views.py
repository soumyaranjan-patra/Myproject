# from django.shortcuts import render

# # Create your views here.
# """
# DRF views: JWT login (with Student login recording), registration, Professor-only APIs.
# """
# from rest_framework import generics, status
# from rest_framework.request import Request
# from rest_framework.response import Response
# from rest_framework.views import APIView

# from rest_framework_simplejwt.views import TokenObtainPairView

# from .models import CustomUser, Department, Role, StudentLogin, StudentProfile
# from .permissions import IsVerifiedProfessor
# from .serializers import (
#     DepartmentSerializer,
#     ProfessorRegisterSerializer,
#     StudentLoginSerializer,
#     StudentProfileListSerializer,
#     StudentRegisterSerializer,
#     UserReadSerializer,
# )


# def get_client_ip(request: Request):
#     """Extract client IP from request."""
#     x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
#     if x_forwarded_for:
#         return x_forwarded_for.split(",")[0].strip()
#     return request.META.get("REMOTE_ADDR")


# def get_user_agent(request: Request):
#     """Extract User-Agent from request."""
#     return request.META.get("HTTP_USER_AGENT", "")[:500]


# # ---------- Custom JWT Login: record Student login (roll_no, department) ----------


# class CustomTokenObtainPairView(TokenObtainPairView):
#     """
#     Override JWT obtain pair so that when a Student logs in we create a
#     StudentLogin record with roll_no and department.
#     """

#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)
#         if response.status_code != 200:
#             return response

#         # Response contains access/refresh tokens; user was authenticated
#         email = request.data.get("email")
#         if not email:
#             return response

#         try:
#             user = CustomUser.objects.get(email=email)
#         except CustomUser.DoesNotExist:
#             return response

#         if user.role == Role.STUDENT:
#             try:
#                 profile = user.student_profile
#             except StudentProfile.DoesNotExist:
#                 return response
#             StudentLogin.objects.create(
#                 user=user,
#                 roll_no=profile.roll_no,
#                 department=profile.department,
#                 ip_address=get_client_ip(request),
#                 user_agent=get_user_agent(request),
#             )
#         return response


# # ---------- Registration ----------


# class ProfessorRegisterView(APIView):
#     """Professor signup. is_active=False and verification_status=PENDING set by signal."""

#     def post(self, request):
#         serializer = ProfessorRegisterSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(
#             {"detail": "Registration successful. Awaiting admin approval."},
#             status=status.HTTP_201_CREATED,
#         )


# class StudentRegisterView(APIView):
#     """Student signup. Active immediately; profile with roll_no, name, department."""

#     def post(self, request):
#         serializer = StudentRegisterSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(
#             {"detail": "Registration successful. You can log in."},
#             status=status.HTTP_201_CREATED,
#         )


# # ---------- Departments (public for registration forms) ----------


# class DepartmentListView(generics.ListAPIView):
#     """List departments (e.g. for registration dropdowns)."""
#     queryset = Department.objects.all()
#     serializer_class = DepartmentSerializer


# # ---------- Professor-only: students in same department ----------


# class StudentListByDepartmentView(generics.ListAPIView):
#     """
#     List students in the same department as the requesting Professor.
#     Permission: IsVerifiedProfessor.
#     """
#     permission_classes = [IsVerifiedProfessor]
#     serializer_class = StudentProfileListSerializer

#     def get_queryset(self):
#         user = self.request.user
#         if not user.department_id:
#             return StudentProfile.objects.none()
#         return StudentProfile.objects.filter(department=user.department).select_related(
#             "user", "department"
#         )


# # ---------- Professor-only: student logins (attendance) in same department ----------


# class StudentLoginListByDepartmentView(generics.ListAPIView):
#     """
#     List student logins for the Professor's department.
#     Permission: IsVerifiedProfessor.
#     """
#     permission_classes = [IsVerifiedProfessor]
#     serializer_class = StudentLoginSerializer

#     def get_queryset(self):
#         user = self.request.user
#         if not user.department_id:
#             return StudentLogin.objects.none()
#         return StudentLogin.objects.filter(department=user.department).select_related(
#             "department"
#         )


# # ---------- Current user (optional) ----------


# class CurrentUserView(APIView):
#     """Return current authenticated user (for frontend)."""

#     def get(self, request):
#         if not request.user.is_authenticated:
#             return Response({"detail": "Not authenticated"}, status=401)
#         serializer = UserReadSerializer(request.user)
#         return Response(serializer.data)


from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import CustomUser, StudentProfile, StudentLoginRecord, Department
from .serializers import (
    ProfessorRegisterSerializer,
    StudentRegisterSerializer,
    DepartmentSerializer,
    UserReadSerializer,
    StudentProfileListSerializer,
    StudentLoginRecordSerializer,
)

# ---------- Registration ----------

class ProfessorRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = ProfessorRegisterSerializer
    permission_classes = [AllowAny]


class StudentRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = StudentRegisterSerializer
    permission_classes = [AllowAny]


# ---------- JWT Login ----------

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            try:
                user = CustomUser.objects.get(email=request.data["email"])

                if user.role == "STUDENT":
                    profile = StudentProfile.objects.get(user=user)

                    StudentLoginRecord.objects.create(
                        student=profile,
                        department=profile.department.name
                    )

            except (CustomUser.DoesNotExist, StudentProfile.DoesNotExist):
                pass

        return response


# ---------- Departments ----------

class DepartmentListView(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [AllowAny]


# ---------- Current User ----------

class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserReadSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ---------- Professor Views ----------

class StudentListByDepartmentView(generics.ListAPIView):
    serializer_class = StudentProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return StudentProfile.objects.filter(department=user.department)


class StudentLoginListByDepartmentView(generics.ListAPIView):
    serializer_class = StudentLoginRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return StudentLoginRecord.objects.filter(student__department=user.department)
