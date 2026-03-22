from django.urls import path
from .views import (
    StudentProfileView,
    StudentProfileCreateView,
    AvailableSubjectsView,
    EnrollSubjectView,
    EnrolledSubjectsView
)

urlpatterns = [
    path('profile/', StudentProfileView.as_view(), name='student-profile'),
    path('profile/create/', StudentProfileCreateView.as_view(), name='student-profile-create'),
    path('subjects/available/', AvailableSubjectsView.as_view(), name='available-subjects'),
    path('subjects/enroll/', EnrollSubjectView.as_view(), name='enroll-subject'),
    path('subjects/enrolled/', EnrolledSubjectsView.as_view(), name='enrolled-subjects'),
]