import re
from collections import namedtuple
from operator import attrgetter
from sklearn import svm
import joblib
from nltk import word_tokenize
from nltk.corpus import stopwords
import unidecode
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework.authtoken.models import Token
from .models import Post
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .serializers import UserDetailSerializer, PostSerializer


def hero_view(request):
    return render(request, 'hero.html')


def posts_view(request):
    posts = Post.objects.all().order_by('-created_at')
    context = {'posts': posts}
    return render(request, 'posts.html', context)


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Username or email already exists."}, status=400)

        user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name,
                                        last_name=last_name)

        token, created = Token.objects.get_or_create(user=user)

        user = authenticate(request, username=username, password=password)
        login(request, user)

        return redirect('login')

    elif request.method == 'GET':
        return render(request, 'register.html')

    return JsonResponse({"error": "Invalid request method."}, status=400)


def handleLogin(request):
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


def user_detail(request):
    user = request.user
    serializer = UserDetailSerializer(user)
    return render(request, 'about.html', {'user_data': serializer.data})


def user_posts(request):
    u_posts = Post.objects.filter(user=request.user).order_by('-created_at')
    context = {'user_posts': u_posts}
    return render(request, 'user_posts.html', context)


def create_post_view(request):
    if request.method == 'POST':
        # Obsługa dodawania nowego posta
        serializer = PostSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return redirect('user_posts')
        else:
            return JsonResponse({"error": "Invalid form data."}, status=400)
    elif request.method == 'GET':
        return render(request, 'create_post.html')
    else:
        return JsonResponse({"error": "Invalid request method."}, status=400)


def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user == post.user:
        post.delete()
        messages.success(request, 'Post deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this post.')

    return HttpResponseRedirect(reverse('user_posts'))


def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user == post.user:
        if request.method == 'POST':
            post.title = request.POST.get('title')
            post.content = request.POST.get('content')
            post.save()

            messages.success(request, 'Post updated successfully.')
            return HttpResponseRedirect(reverse('user_posts'))
        else:
            return render(request, 'edit_post.html', {'post': post})
    else:
        messages.error(request, 'You do not have permission to edit this post.')
        return HttpResponseRedirect(reverse('user_posts'))


loaded_svm_model = joblib.load('emotion_aplication/svm_model.joblib')
loaded_svm_vectorizer = joblib.load('emotion_aplication/svm_vectorizer.joblib')
loaded_svm_label_encoder = joblib.load('emotion_aplication/svm_label_encoder.joblib')


def preprocess_text(text):
    result = text.lower()
    result = result.strip()
    result = re.result = re.sub(r"http\S+", "", result)
    result = re.sub('\S*@\S*\s?', '', result)
    result = unidecode.unidecode(result)
    stop_words = stopwords.words("english")
    word_list = word_tokenize(result)
    # # english stemmer
    # ps = SnowballStemmer("english")

    stemmed_sentence = ""
    for word in word_list:
        if word not in stop_words:
            stemmed_sentence += word
            stemmed_sentence += " "

    result = stemmed_sentence
    whitelist = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    result = ''.join(filter(whitelist.__contains__, result))
    result = ''.join([i for i in result if not i.isdigit()])
    return result


def visualize_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    new_text = post.content
    vectorized_new_text = loaded_svm_vectorizer.transform([preprocess_text(new_text)])

    predictions_proba_svm = loaded_svm_model.predict_proba(vectorized_new_text)

    predicted_label_svm = loaded_svm_label_encoder.inverse_transform(predictions_proba_svm.argmax(axis=1))[0]

    probability_svm = predictions_proba_svm.max()

    Prediction = namedtuple('Prediction', ['label', 'probability'])
    predictions_proba_svm_and_labels = [Prediction(label, prob) for label, prob in
                                        zip(loaded_svm_label_encoder.classes_, predictions_proba_svm[0])]

    predictions_proba_svm_and_labels.sort(key=attrgetter('probability'), reverse=True)

    context = {
        'post': post,
        'predicted_label_svm': predicted_label_svm,
        'probability_svm': probability_svm,
        'predictions_proba_svm_and_labels': predictions_proba_svm_and_labels,
    }

    return render(request, 'visualize_post.html', context)
