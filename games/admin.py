from django.contrib import admin
from .models import Game, GameSession, StudentResponse, Score, Feedback

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'total_levels', 'unity_game_id', 'is_active', 'created_at']
    list_filter = ['subject', 'is_active']
    search_fields = ['name', 'unity_game_id']

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['student', 'game', 'game_level', 'topic', 'status', 'session_start', 'total_questions']
    list_filter = ['status', 'game', 'subject', 'topic', 'game_level']
    search_fields = ['student__full_name']

@admin.register(StudentResponse)
class StudentResponseAdmin(admin.ModelAdmin):
    list_display = ['game_session', 'question', 'is_correct', 'submitted_at']
    list_filter = ['is_correct']

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ['student', 'game_session', 'total_score', 'percentage', 'created_at']
    list_filter = ['created_at']

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['student', 'game_session', 'created_at']
    search_fields = ['student__full_name']