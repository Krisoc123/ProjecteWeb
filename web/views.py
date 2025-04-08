from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib import messages
from django.db import transaction
from .forms import CustomUserCreationForm, LoginForm
from django.contrib.auth.decorators import login_required
from .models import User, Book, Review, Have, Want, SaleDonation, Exchange


# Create your views here.

def home(request):
    return render(request, 'home.html')

def logout_view(request):
    auth_logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('home')

def register_view(request):
    # Si el usuario ya está autenticado, redirigir al inicio
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Toda la lógica de guardado está encapsulada en el método save() del formulario
            # y está protegida por transaction.atomic para evitar registros parciales
            user = form.save()
            # Inicia sesión automáticamente tras el registro
            login(request, user)
            messages.success(request, "Registro completado con éxito.")
            return redirect('home')
        else:
            # Si el formulario no es válido, se mostrarán los errores en la plantilla
            messages.error(request, "Hay errores en el formulario. Por favor, revísalo.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

def login_view(request):
    # If the user is already authenticated, redirect to home
    if request.user.is_authenticated:
        return redirect('home')


    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Wellcome back, {username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

@login_required
def profile_view(request):
    # Get or create a custom User for this auth user
    custom_user, created = User.objects.get_or_create(
        auth_user=request.user,
        defaults={
            'name': request.user.username,
            'email': request.user.email
        }
    )
    
    # Now use custom_user for your queries
    have_list = Have.objects.filter(user=custom_user)
    want_list = Want.objects.filter(user=custom_user)
    exchanges_list = Exchange.objects.filter(user1=custom_user)
    sales_list = SaleDonation.objects.filter(user=custom_user)
    reviews_list = Review.objects.filter(user=custom_user)
    
    context = {
        'django_user': request.user,
        'user': custom_user,
        'have_list': have_list,
        'want_list': want_list,
        'exchanges_list': exchanges_list,
        'sales_list': sales_list,
        'reviews_list': reviews_list,
    }
    
    return render(request, 'profile.html', context)


@login_required
def books(request):
    books = Book.objects.all()
    return render(request, 'books.html', {'books': books})


def trending_view(request):
    return render(request, 'trending.html')

def book_entry(request,ISBN):
    mybook = Book.objects.get(ISBN=ISBN)
    return  render(request,'book-entry.html', {'mybook': mybook})

