from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate

from .decorators import admin_only
from .forms import PostForm, CustomUserCreationForm, ProfileForm, UserForm
from .models import Post, PostComment

# --- VISTAS PÚBLICAS ---

def home(request):
    # Muestra los 3 posts destacados y activos en la página principal
    posts = Post.objects.filter(active=True, featured=True)[0:3]
    
    # Lógica para mostrar siempre el perfil del administrador (tú), protegiendo contra errores
    admin_user = User.objects.filter(is_superuser=True).first()
    profile = None
    if admin_user:
        try:
            profile = admin_user.profile
        except Profile.DoesNotExist:
            profile = None
    
    return render(request, 'base/index.html', {'posts': posts, 'profile': profile})

def posts(request):
    # Muestra todos los posts activos con paginación
    posts_list = Post.objects.filter(active=True)
    page = request.GET.get('page')
    paginator = Paginator(posts_list, 5)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'base/posts.html', {'posts': posts})

def post(request, slug):
    # Muestra un post individual y permite dejar comentarios
    post_obj = Post.objects.get(slug=slug)
    if request.method == 'POST':
        PostComment.objects.create(
            author=request.user.profile,
            post=post_obj,
            body=request.POST['comment']
        )
        messages.success(request, "Tu comentario fue publicado exitosamente!")
        return redirect('post', slug=post_obj.slug)
    return render(request, 'base/post.html', {'post': post_obj})

def profile(request):
    # Muestra el perfil (similar al index pero sin los posts)
    admin_user = User.objects.filter(is_superuser=True).first()
    profile_obj = None
    if admin_user:
        try:
            profile_obj = admin_user.profile
        except Profile.DoesNotExist:
            profile_obj = None
    return render(request, 'base/profile.html', {'profile': profile_obj})

# --- CRUD DE POSTS (Solo para superusuarios) ---

@admin_only
@login_required(login_url="home")
def createPost(request):
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('posts')
    return render(request, 'base/post_form.html', {'form': form})

@admin_only
@login_required(login_url="home")
def updatePost(request, slug):
    post_obj = Post.objects.get(slug=slug)
    form = PostForm(instance=post_obj)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post_obj)
        if form.is_valid():
            form.save()
        return redirect('posts')
    return render(request, 'base/post_form.html', {'form': form})

@admin_only
@login_required(login_url="home")
def deletePost(request, slug):
    post_obj = Post.objects.get(slug=slug)
    if request.method == 'POST':
        post_obj.delete()
        return redirect('posts')
    return render(request, 'base/delete.html', {'item': post_obj})

# --- ENVÍO DE CORREO ---

def sendEmail(request):
    if request.method == 'POST':
        template = render_to_string('base/email_template.html', {
            'name': request.POST['name'],
            'email': request.POST['email'],
            'message': request.POST['message'],
        })
        email = EmailMessage(
            request.POST['subject'],
            template,
            settings.DEFAULT_FROM_EMAIL,
            ['alijcolina@gmail.com']
        )
        email.fail_silently = False
        email.send()
    return render(request, 'base/email_sent.html')

# --- AUTENTICACIÓN ---

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            messages.error(request, 'El usuario con este email no existe')
            return redirect('login')
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Email o contraseña incorrectos')
    return render(request, 'base/login.html', {})

def registerPage(request):
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            messages.success(request, 'Cuenta creada exitosamente!')
            user = authenticate(request, username=user.username, password=request.POST['password1'])
            if user is not None:
                login(request, user)
            next_url = request.GET.get('next')
            if next_url == '' or next_url is None:
                next_url = 'home'
            return redirect(next_url)
        else:
            messages.error(request, 'Ocurrió un error en el registro')
    return render(request, 'base/register.html', {'form': form})

def logoutUser(request):
    logout(request)
    return redirect('home')

@login_required(login_url="home")
def userAccount(request):
    profile_obj = request.user.profile
    return render(request, 'base/account.html', {'profile': profile_obj})

@login_required(login_url="home")
def updateProfile(request):
    user = request.user
    profile_obj = user.profile
    form = ProfileForm(instance=profile_obj)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            return redirect('account')
    return render(request, 'base/profile_form.html', {'form': form})