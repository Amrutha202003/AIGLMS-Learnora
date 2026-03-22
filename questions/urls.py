from django.urls import path
from .views import (
    AIGenerateQuestionsView,
    BulkGenerateQuestionsView,
    GetQuestionsForGameView  # ← ADD THIS
)

urlpatterns = [
    path('ai/generate/', AIGenerateQuestionsView.as_view(), name='ai-generate-questions'),
    path('ai/bulk-generate/', BulkGenerateQuestionsView.as_view(), name='bulk-generate-questions'),
    path('game-questions/', GetQuestionsForGameView.as_view(), name='game-questions'),  # ← ADD THIS
]