from django.urls import path
from .views import hero_view, posts_view, register, handleLogin, logout_view

urlpatterns = [
    path('', hero_view, name='hero_view'),
    path('posts/', posts_view, name='posts'),
    path('register/', register, name='register'),
    path('login/', handleLogin, name='login'),
    path('logout/', logout_view, name='logout'),
]
