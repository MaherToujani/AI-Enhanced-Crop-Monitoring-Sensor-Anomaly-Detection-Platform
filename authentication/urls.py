from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView

from .views import LoginView, MeView, RefreshTokenView, RegisterView


urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/refresh/", RefreshTokenView.as_view(), name="auth-refresh"),
    path("auth/verify/", TokenVerifyView.as_view(), name="auth-verify"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
]



