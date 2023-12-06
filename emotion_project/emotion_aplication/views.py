from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.authtoken.models import Token

from .models import Post  # Assuming you have a Post model in your models.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages


def hero_view(request):
    return render(request, 'hero.html')


def posts_view(request):
    # Fetch posts from the database
    posts = Post.objects.all().order_by('-created_at')

    # Pass the posts to the template
    context = {'posts': posts}
    return render(request, 'posts.html', context)


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        # Check if the username or email already exists
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Username or email already exists."}, status=400)

        # Create a new user
        user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)

        # Create a Token for the user
        token, created = Token.objects.get_or_create(user=user)

        # Log in the user
        user = authenticate(request, username=username, password=password)
        login(request, user)

        # Redirect to the login page
        return redirect('login')

    elif request.method == 'GET':
        # Render the registration form
        return render(request, 'register.html')

    return JsonResponse({"error": "Invalid request method."}, status=400)


def handleLogin(request):
    # Your existing login logic here
    email = request.POST.get("email")
    password = request.POST.get("password")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # messages.error(request, 'Invalid login credentials. Please try again.')
        return render(request, 'login.html')

    if not user.check_password(password):
        # messages.error(request, 'Invalid login credentials. Please try again.')
        return render(request, 'login.html')

    user = authenticate(username=user.username, password=password)

    if user:
        login(request, user)
        messages.success(request, 'Successfully logged in!')
        return redirect('hero_view')  # Redirect to the home page after successful login
    else:
        # messages.error(request, 'Invalid login credentials. Please try again.')
        return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

