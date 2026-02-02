from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='admin/password_reset_form.html',
        email_template_name='admin/password_reset_email.html',
        subject_template_name='admin/password_reset_subject.txt',
        success_url='/password_reset/done/'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='admin/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='admin/password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='admin/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Reception URLs
    path('reception/rooms/', views.reception_rooms_view, name='reception_rooms'),
    path('reception/reservations/', views.reception_reservations_view, name='reception_reservations'),
    path('reception/reservations/new/', views.reception_reservation_create_view, name='reception_reservation_create'),
    path('reception/reservations/<int:pk>/status/<str:new_status>/', views.reception_reservation_update_status, name='reception_reservation_status'),
]
