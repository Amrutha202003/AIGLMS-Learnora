from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserRegistrationView, UserLoginView, UserProfileView

urlpatterns = [
    # Auth API endpoints (called by JS / Unity)
    path('register/',      UserRegistrationView.as_view(), name='api_register'),
    path('login/',         UserLoginView.as_view(),        name='api_login'),
    path('profile/',       UserProfileView.as_view(),      name='api_profile'),
    path('token/refresh/', TokenRefreshView.as_view(),     name='token_refresh'),
]