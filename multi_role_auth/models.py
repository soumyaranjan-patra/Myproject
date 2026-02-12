
# from django.db import models

# # Create your models here.
# """
# Multi-role user system: Custom User with ADMIN, PROFESSOR, STUDENT roles.
# Professor verification workflow, Student profiles, and login/attendance tracking.
# """
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# from django.db import models
# from django.utils import timezone


# class Role(models.TextChoices):
#     ADMIN = "ADMIN", "Admin"
#     PROFESSOR = "PROFESSOR", "Professor"
#     STUDENT = "STUDENT", "Student"


# class VerificationStatus(models.TextChoices):
#     PENDING = "PENDING", "Pending"
#     APPROVED = "APPROVED", "Approved"
#     REJECTED = "REJECTED", "Rejected"


# class Department(models.Model):
#     """Department model - students and professors belong to departments."""
#     name = models.CharField(max_length=100, unique=True)
#     code = models.CharField(max_length=20, unique=True, blank=True)

#     class Meta:
#         ordering = ["name"]

#     def __str__(self):
#         return self.name


# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError("Users must have an email address")
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault("is_staff", True)
#         extra_fields.setdefault("is_superuser", True)
#         extra_fields.setdefault("role", Role.ADMIN)
#         if extra_fields.get("is_staff") is not True:
#             raise ValueError("Superuser must have is_staff=True.")
#         if extra_fields.get("is_superuser") is not True:
#             raise ValueError("Superuser must have is_superuser=True.")
#         return self.create_user(email, password, **extra_fields)


# class CustomUser(AbstractBaseUser, PermissionsMixin):
#     """
#     Custom User with roles: ADMIN, PROFESSOR, STUDENT.
#     Professors start with is_active=False and verification_status=PENDING.
#     """
#     email = models.EmailField(unique=True)
#     first_name = models.CharField(max_length=150, blank=True)
#     last_name = models.CharField(max_length=150, blank=True)
#     role = models.CharField(
#         max_length=20,
#         choices=Role.choices,
#         default=Role.STUDENT,
#     )
#     is_staff = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
#     date_joined = models.DateTimeField(default=timezone.now)

#     # Professor-specific: set on signup, used for approval workflow
#     verification_status = models.CharField(
#         max_length=20,
#         choices=VerificationStatus.choices,
#         default=VerificationStatus.PENDING,
#         blank=True,
#     )
#     department = models.ForeignKey(
#         Department,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="users",
#     )

#     objects = CustomUserManager()

#     USERNAME_FIELD = "email"
#     REQUIRED_FIELDS = []

#     class Meta:
#         verbose_name = "user"
#         verbose_name_plural = "users"

#     def __str__(self):
#         return self.email

#     @property
#     def is_verified_professor(self):
#         return (
#             self.role == Role.PROFESSOR
#             and self.verification_status == VerificationStatus.APPROVED
#             and self.is_active
#         )


# class StudentProfile(models.Model):
#     """
#     Student profile: roll_no, department, name.
#     Students are active immediately; visible to Professors only in same department.
#     """
#     user = models.OneToOneField(
#         CustomUser,
#         on_delete=models.CASCADE,
#         related_name="student_profile",
#     )
#     roll_no = models.CharField(max_length=50, unique=True)
#     name = models.CharField(max_length=255)
#     department = models.ForeignKey(
#         Department,
#         on_delete=models.CASCADE,
#         related_name="students",
#     )

#     class Meta:
#         ordering = ["roll_no"]

#     def __str__(self):
#         return f"{self.name} ({self.roll_no})"


# class StudentLogin(models.Model):
#     """
#     Records each student login: roll_no, department, timestamp.
#     Professors can view logins for students in their department.
#     """
#     user = models.ForeignKey(
#         CustomUser,
#         on_delete=models.CASCADE,
#         related_name="login_records",
#         null=True,
#         blank=True,
#     )
#     roll_no = models.CharField(max_length=50)
#     department = models.ForeignKey(
#         Department,
#         on_delete=models.CASCADE,
#         related_name="student_logins",
#     )
#     login_at = models.DateTimeField(default=timezone.now)
#     ip_address = models.GenericIPAddressField(null=True, blank=True)
#     user_agent = models.CharField(max_length=500, blank=True)

#     class Meta:
#         ordering = ["-login_at"]
#         verbose_name = "Student login"
#         verbose_name_plural = "Student logins"

#     def __str__(self):
#         return f"{self.roll_no} @ {self.login_at}"

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


# ----------------------
# Department Model
# ----------------------
class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


# ----------------------
# Custom User Manager
# ----------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


# ----------------------
# Custom User Model
# ----------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('PROFESSOR', 'Professor'),
        ('STUDENT', 'Student'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    verification_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


# ----------------------
# Student Profile
# ----------------------
class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    roll_no = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.roll_no


# ----------------------
# Professor Profile
# ----------------------
class ProfessorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    cabin_number = models.CharField(max_length=100)

    def __str__(self):
        return f"Prof. {self.user.email}"


# ----------------------
# Login Record
# ----------------------
class StudentLoginRecord(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    login_at = models.DateTimeField(auto_now_add=True)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.student.roll_no} - {self.login_at}"
