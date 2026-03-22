from django.urls import path
from .views import (
    StartGameSessionView,
    SubmitAnswerView,
    EndGameSessionView,
    GameSessionDetailView,
    StudentScoresView,
    StudentProgressView,
    StudentFeedbackView,
    GetCurrentTopicView    # ← ADD THIS
)

urlpatterns = [
    path('start-session/', StartGameSessionView.as_view(), name='start-game-session'),
    path('submit-answer/', SubmitAnswerView.as_view(), name='submit-answer'),
    path('end-session/', EndGameSessionView.as_view(), name='end-game-session'),
    path('session/<int:pk>/', GameSessionDetailView.as_view(), name='game-session-detail'),
    path('scores/', StudentScoresView.as_view(), name='student-scores'),
    path('progress/', StudentProgressView.as_view(), name='student-progress'),
    path('feedback/<int:session_id>/', StudentFeedbackView.as_view(), name='session-feedback'),
    path('current-topic/', GetCurrentTopicView.as_view(), name='current-topic'),  # ← ADD THIS
]