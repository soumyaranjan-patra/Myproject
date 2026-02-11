"""
URL configuration for multi_role_auth.
Use SimpleJWT for token obtain/refresh; custom obtain view records Student logins.
"""
from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = "multi_role_auth"

urlpatterns = [
    # JWT: use custom obtain to record Student login (roll_no, department)
    path("token/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Registration
    path("register/professor/", views.ProfessorRegisterView.as_view(), name="register_professor"),
    path("register/student/", views.StudentRegisterView.as_view(), name="register_student"),
    # Public
    path("departments/", views.DepartmentListView.as_view(), name="department_list"),
    # Current user
    path("me/", views.CurrentUserView.as_view(), name="current_user"),
    # Professor-only (IsVerifiedProfessor)
    path(
        "students/",
        views.StudentListByDepartmentView.as_view(),
        name="student_list_by_department",
    ),
    path(
        "student-logins/",
        views.StudentLoginListByDepartmentView.as_view(),
        name="student_login_list_by_department",
    ),
]
