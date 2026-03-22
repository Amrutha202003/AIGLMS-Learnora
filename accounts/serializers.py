from rest_framework import serializers
from django.contrib.auth import get_user_model
from students.models import StudentProfile

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password         = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    full_name        = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model  = User
        fields = [
            'username',
            'email',
            'phone_number',
            'full_name',
            'password',
            'password_confirm',
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "This username is already taken.")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        full_name = validated_data.pop('full_name', '')

        # Create the User — post_save signal auto-creates StudentProfile
        user = User.objects.create_user(
            username     = validated_data['username'],
            email        = validated_data['email'],
            phone_number = validated_data.get('phone_number', ''),
            password     = validated_data['password'],
            is_student   = True,
        )

        # FIX: only update fields that actually exist on StudentProfile.
        # We only know 'full_name' exists for sure.
        # email/phone are NOT on StudentProfile — removed to prevent FieldError.
        if full_name:
            try:
                profile = StudentProfile.objects.get(user=user)
                profile.full_name = full_name
                profile.save()
            except StudentProfile.DoesNotExist:
                # Signal may not have run yet in some edge cases
                StudentProfile.objects.create(
                    user=user,
                    full_name=full_name
                )

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model            = User
        fields           = ['id', 'username', 'email',
                            'phone_number', 'is_student', 'date_joined']
        read_only_fields = ['id', 'date_joined']