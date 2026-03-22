from rest_framework import serializers
from .models import StudentProfile
from academics.models import Subject

class StudentProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for student profile
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'full_name', 'board', 'grade', 'profile_image', 
                  'user_email', 'user_phone', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class StudentProfileCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating student profile
    """
    class Meta:
        model = StudentProfile
        fields = ['full_name', 'board', 'grade', 'profile_image']