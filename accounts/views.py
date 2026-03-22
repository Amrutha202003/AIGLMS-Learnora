# ─────────────────────────────────────────────────────────────
# FILE LOCATION: gamified_lms/accounts/views.py
# REPLACE the entire contents of this file with the code below
# ─────────────────────────────────────────────────────────────

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404

from .serializers import UserRegistrationSerializer, UserSerializer
from .models import User
from students.models import StudentProfile


# ═══════════════════════════════════════════════════════════════
# API VIEWS
# ═══════════════════════════════════════════════════════════════

class UserRegistrationView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    """
    permission_classes = [AllowAny]
    serializer_class   = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            errors      = serializer.errors
            first_error = next(iter(errors.values()))
            message     = first_error[0] if isinstance(first_error, list) \
                          else str(first_error)
            return Response(
                {'error': message},
                status=status.HTTP_400_BAD_REQUEST
            )

        user    = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response({
            'user':    UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access':  str(refresh.access_token),
            },
            'message': 'Account created successfully!'
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """
    POST /api/auth/login/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()

        if not username or not password:
            return Response(
                {'error': 'Please provide both username and password.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Support login with email OR username
        user = None
        if '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(
                    request,
                    username=user_obj.username,
                    password=password
                )
            except User.DoesNotExist:
                pass
        else:
            user = authenticate(request, username=username, password=password)

        if not user:
            return Response(
                {'error': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'error': 'Account is not active. Please verify your email.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # FIX: only pass 'full_name' to StudentProfile — no email/phone
        # because StudentProfile model does not have those fields
        StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'full_name': user.get_full_name() or user.username,
            }
        )

        refresh = RefreshToken.for_user(user)

        return Response({
            'user':    UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access':  str(refresh.access_token),
            },
            'message': 'Login successful!'
        }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveAPIView):
    """
    GET /api/auth/profile/
    """
    permission_classes = [IsAuthenticated]
    serializer_class   = UserSerializer

    def get_object(self):
        return self.request.user


# ═══════════════════════════════════════════════════════════════
# PAGE VIEWS  (render HTML templates)
# ═══════════════════════════════════════════════════════════════

def home_page(request):
    return render(request, 'public/home.html')

def login_page(request):
    return render(request, 'accounts/login.html')

def register_page(request):
    return render(request, 'accounts/register.html')

def select_topic_page(request):
    return render(request, 'select_topic.html')

def dashboard_page(request):
    return render(request, 'dashboard/dashboard.html')

def game_page(request):
    return render(request, 'game/game.html')

def logout_view(request):
    logout(request)
    return redirect('login_page')


# ═══════════════════════════════════════════════════════════════
# EMAIL VERIFICATION
# ═══════════════════════════════════════════════════════════════

def verify_email(request, uid, token):
    user = get_object_or_404(User, pk=uid)
    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Email verified! You can now log in.")
        return redirect('login_page')
    messages.error(request, "Verification link is invalid or has expired.")
    return redirect('home')