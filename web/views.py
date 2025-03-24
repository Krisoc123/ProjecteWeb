from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User, Book, Review, Tengo, Quiero, VendaDonacio, Intercanvi
import requests

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
    # Obtenim els paràmetres de cerca
    author = request.GET.get('author', '')
    title = request.GET.get('title', '')
    topic = request.GET.get('topic', '')
    
    # Filtrem els llibres locals
    queryset = Book.objects.all()
    
    if author:
        queryset = queryset.filter(author__icontains=author)
    
    if title:
        queryset = queryset.filter(title__icontains=title)
    
    if topic:
        queryset = queryset.filter(topic=topic)
    
    # Obtenim llibres d'APIs externes si hi ha paràmetres de cerca
    external_books = []
    if author or title:
        # Cerca a Google Books API
        search_term = f"{title} {author}".strip()
        print(f"Cercant amb el terme: '{search_term}'")  # Logging
        if search_term:
            try:
                api_url = f"https://www.googleapis.com/books/v1/volumes?q={search_term}&maxResults=6"
                print(f"Cridant API: {api_url}")  # Logging
                google_response = requests.get(api_url)
                print(f"Codi de resposta: {google_response.status_code}")  # Logging
                
                if google_response.status_code == 200:
                    data = google_response.json()
                    print(f"Resultats obtinguts: {len(data.get('items', []))}")  # Logging
                    for item in data.get('items', []):
                        volume_info = item.get('volumeInfo', {})
                        external_books.append({
                            'title': volume_info.get('title', 'Unknown Title'),
                            'author': ', '.join(volume_info.get('authors', ['Unknown Author'])),
                            'description': volume_info.get('description', ''),
                            'thumbnail_url': volume_info.get('imageLinks', {}).get('thumbnail', ''),
                            'isbn': volume_info.get('industryIdentifiers', [{}])[0].get('identifier', ''),
                            'external_link': volume_info.get('infoLink', ''),
                            'source': 'Google Books'
                        })
            except Exception as e:
                print(f"Error fetching from Google Books API: {e}")
    
    context = {
        'books': queryset,
        'external_books': external_books
    }
    
    return render(request, 'books.html', context)