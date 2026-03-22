from django.contrib import admin
from .models import Subject, Topic, Concept, StudentSubject

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'board', 'grade', 'is_active']
    list_filter = ['board', 'grade', 'is_active']
    search_fields = ['name']

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'difficulty_level', 'order']
    list_filter = ['difficulty_level', 'subject']
    search_fields = ['name']

@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):
    list_display = ['name', 'topic']
    search_fields = ['name']

@admin.register(StudentSubject)
class StudentSubjectAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'enrolled_at', 'is_active']
    list_filter = ['is_active']