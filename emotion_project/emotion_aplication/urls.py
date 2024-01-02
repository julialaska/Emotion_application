from django.urls import path
from .views import hero_view, posts_view, register, handleLogin, logout_view, user_detail, user_posts, create_post_view, delete_post, edit_post, visualize_post, user_emotions_summary


urlpatterns = [
    path('', hero_view, name='hero_view'),
    path('posts/', posts_view, name='posts'),
    path('register/', register, name='register'),
    path('login/', handleLogin, name='login'),
    path('logout/', logout_view, name='logout'),
    path('about/', user_detail, name='user_detail'),
    path('my_posts/', user_posts, name='user_posts'),
    path('create_post/', create_post_view, name='create_post_view'),
    path('delete_post/<int:post_id>/', delete_post, name='delete_post'),
    path('visualize_post/<int:post_id>/', visualize_post, name='visualize_post'),
    path('emotions/', user_emotions_summary, name='user_emotions_summary'),
    path('edit_post/<int:post_id>/', edit_post, name='edit_post'),
]
