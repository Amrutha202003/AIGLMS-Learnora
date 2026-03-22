from django.contrib import admin
from .models import Question, Answer

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'topic', 'question_type', 'difficulty_level', 'marks']
    list_filter = ['question_type', 'difficulty_level', 'topic']
    search_fields = ['question_text']
    inlines = [AnswerInline]

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'answer_text', 'is_correct']
    list_filter = ['is_correct']