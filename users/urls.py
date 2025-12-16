from django.urls import path
from . import views

# app_name = "users"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    # path("activate/<uidb64>/<token>/", views.activate_account, name="activate"),
    
    path('dashboard/', views.dashboard, name='dashboard'),



]


from django.contrib.auth import views as auth_views

urlpatterns += [

    # Password Reset Request
    path("password-reset/", 
         auth_views.PasswordResetView.as_view(
             template_name="users/password_reset.html"
         ),
         name="password_reset"),

    # Password Reset Email Sent
    path("password-reset/done/", 
         auth_views.PasswordResetDoneView.as_view(
             template_name="users/password_reset_done.html"
         ),
         name="password_reset_done"),

    # Password Reset Confirm
    path("reset/<uidb64>/<token>/", 
         auth_views.PasswordResetConfirmView.as_view(
             template_name="users/password_reset_confirm.html"
         ),
         name="password_reset_confirm"),

    # Password Reset Complete
    path("reset/done/", 
         auth_views.PasswordResetCompleteView.as_view(
             template_name="users/password_reset_complete.html"
         ),
         name="password_reset_complete"),
]
