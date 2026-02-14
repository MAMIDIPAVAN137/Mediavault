from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core.views import (
    home, signup_view, login_view, profile, request_upload_access, 
    edit_profile, delete_account, admin_dashboard, admin_upload_requests,
    toggle_profile_privacy, update_theme, admin_edit_user, report_problem,
    update_username, verify_password,
    admin_user_list, admin_media_list, search_users
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Profile & Settings
    path('profile/', profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/delete/', delete_account, name='delete_account'),
    path('profile/privacy/toggle/', toggle_profile_privacy, name='toggle-profile-privacy'),
    path('profile/theme/update/', update_theme, name='update-theme'),
    path('profile/report-problem/', report_problem, name='report-problem'),
    path('profile/username/update/', update_username, name='update-username'),
    path('profile/verify-password/', verify_password, name='verify-password'),
    path('api/users/search/', search_users, name='search-users'),
    path('profile/<str:username>/', profile, name='user_profile'),
    
    # Password Change
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change_form.html',
        success_url='/password-change/done/'
    ), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'
    ), name='password_change_done'),

    # Admin Portal
    path('portal/admin/', admin_dashboard, name='admin_dashboard'),
    path('portal/admin/requests/', admin_upload_requests, name='admin_upload_requests'),
    path('portal/admin/user/<str:username>/edit/', admin_edit_user, name='admin_edit_user'),
    path('portal/admin/users/', admin_user_list, name='admin_user_list'),
    path('portal/admin/media/', admin_media_list, name='admin_media_list'),
    
    # App URLs
    path('upload-request/', request_upload_access, name='request_upload_access'),
    path('api/media/', include('media.urls')),
    path('api/social/', include('social.urls')),
    path('api/stats/', include('stats.urls')),
    path('chat/', include('chat.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
