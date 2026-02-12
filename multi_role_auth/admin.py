

# # Register your models here.
# """
# Admin: Professors visible for approval (is_active, verification_status).
# Students and Departments manageable; Student logins read-only list.
# """
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# from .models import CustomUser, Department, Role, StudentLogin, StudentProfile, VerificationStatus


# @admin.register(Department)
# class DepartmentAdmin(admin.ModelAdmin):
#     list_display = ["name", "code"]
#     search_fields = ["name", "code"]


# @admin.register(CustomUser)
# class CustomUserAdmin(BaseUserAdmin):
#     list_display = [
#         "email",
#         "first_name",
#         "last_name",
#         "role",
#         "verification_status",
#         "is_active",
#         "department",
#         "date_joined",
#     ]
#     list_filter = ["role", "verification_status", "is_active", "department"]
#     search_fields = ["email", "first_name", "last_name"]
#     ordering = ["-date_joined"]
#     filter_horizontal = []
#     fieldsets = (
#         (None, {"fields": ("email", "password")}),
#         ("Personal", {"fields": ("first_name", "last_name")}),
#         (
#             "Role & Access",
#             {
#                 "fields": (
#                     "role",
#                     "department",
#                     "verification_status",
#                     "is_active",
#                     "is_staff",
#                     "is_superuser",
#                 )
#             },
#         ),
#         ("Dates", {"fields": ("last_login", "date_joined")}),
#     )
#     add_fieldsets = (
#         (
#             None,
#             {
#                 "classes": ("wide",),
#                 "fields": ("email", "password1", "password2"),
#             },
#         ),
#     )

#     actions = ["approve_professors", "reject_professors"]

#     @admin.action(description="Approve selected professors")
#     def approve_professors(self, request, queryset):
#         updated = queryset.filter(role=Role.PROFESSOR).update(
#             verification_status=VerificationStatus.APPROVED,
#             is_active=True,
#         )
#         self.message_user(request, f"Approved {updated} professor(s).")

#     @admin.action(description="Reject selected professors")
#     def reject_professors(self, request, queryset):
#         updated = queryset.filter(role=Role.PROFESSOR).update(
#             verification_status=VerificationStatus.REJECTED,
#             is_active=False,
#         )
#         self.message_user(request, f"Rejected {updated} professor(s).")


# @admin.register(StudentProfile)
# class StudentProfileAdmin(admin.ModelAdmin):
#     list_display = ["roll_no", "name", "department", "user"]
#     list_filter = ["department"]
#     search_fields = ["roll_no", "name", "user__email"]


# @admin.register(StudentLogin)
# class StudentLoginAdmin(admin.ModelAdmin):
#     list_display = ["roll_no", "department", "login_at", "ip_address"]
#     list_filter = ["department", "login_at"]
#     search_fields = ["roll_no"]
#     readonly_fields = ["user", "roll_no", "department", "login_at", "ip_address", "user_agent"]
#     date_hierarchy = "login_at"

#     def has_add_permission(self, request):
#         return False

from django.contrib import admin
from .models import CustomUser, Department, StudentProfile, StudentLoginRecord, ProfessorProfile


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'verification_status', 'is_active')
    list_filter = ('role', 'verification_status')
    list_editable = ('role',)
    actions = ['approve_professors']

    def approve_professors(self, request, queryset):
        queryset.update(verification_status='APPROVED', is_active=True)

    approve_professors.short_description = "Approve selected Professors"


admin.site.register(Department)
admin.site.register(StudentProfile)
admin.site.register(StudentLoginRecord)
admin.site.register(ProfessorProfile)
