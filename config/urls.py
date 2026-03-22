from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import (
    home_page,
    login_page,
    register_page,
    logout_view,
    dashboard_page,
    select_topic_page,
    game_page,          # FIX: was wrongly imported from 'game.views' — doesn't exist
                        #      game_page lives in accounts.views
)

urlpatterns = [
    path('admin/',        admin.site.urls),

    # ── Page routes ──────────────────────────────────────
    path('',              home_page,          name='home'),
    path('login/',        login_page,         name='login_page'),
    path('register/',     register_page,      name='register'),
    path('dashboard/',    dashboard_page,     name='dashboard'),
    path('select-topic/', select_topic_page,  name='select_topic'),
    path('play-game/',    game_page,          name='play_game'),
    path('logout/',       logout_view,        name='logout'),

    # ── API routes ────────────────────────────────────────
    path('api/auth/',      include('accounts.urls')),
    path('api/student/',   include('students.urls')),
    path('api/academics/', include('academics.urls')),
    path('api/game/',      include('games.urls')),
    path('api/questions/', include('questions.urls')),
    path('student/',       include('students.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )