from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User, Book, Review, Tengo, Quiero, VendaDonacio, Intercanvi


# Create your views here.

def home(request):
    return render(request, 'home.html')

def logout_view(request):
    auth_logout(request)
    return redirect('home')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

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
    tengo_list = Tengo.objects.filter(user=custom_user)
    quiero_list = Quiero.objects.filter(user=custom_user)
    intercanvis_list = Intercanvi.objects.filter(user1=custom_user)
    ventas_list = VendaDonacio.objects.filter(user=custom_user)
    reviews_list = Review.objects.filter(user=custom_user)
    
    context = {
        'django_user': request.user,
        'user': custom_user,
        'tengo_list': tengo_list,
        'quiero_list': quiero_list,
        'intercanvis_list': intercanvis_list,
        'ventas_list': ventas_list,
        'reviews_list': reviews_list,
    }
    
    return render(request, 'profile.html', context)


@login_required
def books(request):
    books = Book.objects.all()
    return render(request, 'books.html', {'books': books})