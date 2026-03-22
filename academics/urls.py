from django.urls import path
from .views import (
    SubjectListView,
    SubjectDetailView,
    TopicListView,
    TopicDetailView,
    ConceptListView
)

urlpatterns = [
    path('subjects/', SubjectListView.as_view(), name='subject-list'),
    path('subjects/<int:pk>/', SubjectDetailView.as_view(), name='subject-detail'),
    path('subjects/<int:subject_id>/topics/', TopicListView.as_view(), name='topic-list'),
    path('topics/<int:pk>/', TopicDetailView.as_view(), name='topic-detail'),
    path('topics/<int:topic_id>/concepts/', ConceptListView.as_view(), name='concept-list'),
]