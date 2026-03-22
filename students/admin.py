from django.contrib import admin
from .models import StudentProfile

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'board', 'grade', 'user', 'created_at']
    list_filter = ['board', 'grade']
    search_fields = ['full_name', 'user__email']