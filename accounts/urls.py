from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


app_name = 'accounts'
urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('activate/<str:token>/', views.UserActivateView.as_view(), name='activate'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('profile/', views.UserView.as_view(), name='profile'),
    path('profile/update/', views.UserView.as_view(), name='profile_update'),
    path('password/change/', views.UserPasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', views.UserPasswordResetView.as_view(), name='password_reset'),
    path('password/reset/confirm/<str:token>/', views.UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]