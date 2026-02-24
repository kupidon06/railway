"""
URL configuration for Djengoo authentication in client app
"""

from django.urls import path
from . import views

app_name = 'djengoo'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.djengoo_login, name='login'),
    path('callback/', views.callback, name='callback'),
    path("callback", views.callback, name="callback_no_slash"),
    path('logout/', views.logout_view, name='logout'),
    path('token-info/', views.token_info, name='token_info'),
]
