"""
DRF serializers for multi-role auth: registration, profiles, login records.
"""



from .models import CustomUser, StudentProfile, Department
from rest_framework import serializers
# multi_role_auth/serializers.py
from .models import CustomUser, StudentProfile, Department # Removed Role

from .models import (
    CustomUser,
    Department,
    StudentProfile,
    StudentLoginRecord
    
)


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "code"]


# ---------- User & Auth ----------


class UserReadSerializer(serializers.ModelSerializer):
    """Safe read serializer for user (no password)."""
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "verification_status",
            "department",
            "department_name",
            "date_joined",
        ]
        read_only_fields = fields


class ProfessorRegisterSerializer(serializers.ModelSerializer):
    """Professor registration: email, password, department, name."""
    password = serializers.CharField(write_only=True, min_length=8)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        required=True,
    )

    class Meta:
        model = CustomUser
        fields = ["email", "password", "first_name", "last_name", "department"]

    def create(self, validated_data):
        validated_data["role"] = 'PROFESSOR'
        # is_active and verification_status are set by signal
        user = CustomUser.objects.create_user(**validated_data)
        return user


class StudentRegisterSerializer(serializers.ModelSerializer):
    """Student registration: email, password + StudentProfile (roll_no, name, department)."""
    password = serializers.CharField(write_only=True, min_length=8)
    roll_no = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=255)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        required=True,
    )

    class Meta:
        model = CustomUser
        fields = ["email", "password", "roll_no", "name", "department"]

    def create(self, validated_data):
        roll_no = validated_data.pop("roll_no")
        name = validated_data.pop("name")
        department = validated_data.pop("department")
        validated_data["role"] = "STUDENT"
        user = CustomUser.objects.create_user(**validated_data)
        StudentProfile.objects.create(user=user, roll_no=roll_no, name=name, department=department)
        return user


# ---------- Student (for Professor view) ----------


class StudentProfileListSerializer(serializers.ModelSerializer):
    """Student list for professors (same department only)."""
    department_name = serializers.CharField(source="department.name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = StudentProfile
        fields = ["id", "user", "email", "roll_no", "name", "department", "department_name"]


# ---------- Login / Attendance ----------


class StudentLoginRecordSerializer(serializers.ModelSerializer):
    """Serializer for student login records (attendance)."""
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = StudentLoginRecord
        fields = [
            "id",
            "roll_no",
            "department",
            "department_name",
            "login_at",
            "ip_address",
            "user_agent",
        ]
        read_only_fields = fields

