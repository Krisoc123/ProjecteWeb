from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib import messages
from django.db import transaction
from .forms import CustomUserCreationForm, LoginForm, WantForm, HaveForm
from django.contrib.auth.decorators import login_required
from .models import User, Book, Review, Have, Want, SaleDonation, Exchange
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
import datetime

import requests

# Create your views here.

def home(request):
    return render(request, 'home.html')

def logout_view(request):
    auth_logout(request)
    messages.info(request, "Successfully logged out.")
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
            messages.success(request, "Registration successful! You are now logged in.")
            return redirect('home')
        else:
            # Si el formulario no es válido, se mostrarán los errores en la plantilla
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})

def login_view(request):
    # If the user is already authenticated, redirect to home
    if request.user.is_authenticated:
        return redirect('home')
        
    # If the request is a POST means the user is trying to log in
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
    # If the request is a GET, we just show the login form
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
                api_url = f"https://www.googleapis.com/books/v1/volumes?q={search_term}&maxResults=20"
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

def trending_view(request):
    return render(request, 'trending.html')

class CreateWantView(LoginRequiredMixin, CreateView):
    model = Want
    form_class = WantForm
    template_name = 'want_form.html'
    success_url = reverse_lazy('books')

    def get_initial(self):
        initial = super().get_initial()
        # Recollim dades del llibre dels paràmetres GET
        initial['isbn'] = self.request.GET.get('isbn', '')
        initial['title'] = self.request.GET.get('title', '')
        initial['author'] = self.request.GET.get('author', '')
        initial['topic'] = self.request.GET.get('topic', '')
        return initial

    def form_valid(self, form):
        isbn = form.cleaned_data.get('isbn')
        title = form.cleaned_data.get('title')
        author = form.cleaned_data.get('author')
        topic = form.cleaned_data.get('topic')

        # Si el llibre no existeix a la nostra BD, l'afegim
        try:
            book = Book.objects.get(ISBN=isbn)
        except Book.DoesNotExist:
            # Creem un nou llibre a la base de dades
            book = Book(
                ISBN=isbn,
                title=title,
                author=author,
                topic=topic or "General",
                publish_date=timezone.now().date(),  # Data actual com a predeterminada
                base_price=10  # Preu base predeterminat
            )
            book.save()

        # Obtenim l'usuari actual i li assignem al want
        custom_user = User.objects.get(auth_user=self.request.user)

        # Comprovar si ja existeix un want per aquest usuari i llibre
        existing_want = Want.objects.filter(user=custom_user, book=book).first()

        if existing_want:
            # Actualitzar la prioritat si ja existeix
            existing_want.priority = form.cleaned_data['priority']
            existing_want.save()
        else:
            # Crear un nou want
            want = form.save(commit=False)
            want.user = custom_user
            want.book = book
            want.save()

        return redirect(self.success_url)

class CreateHaveView(LoginRequiredMixin, CreateView):
    model = Have
    form_class = HaveForm  # Canviat de WantForm a HaveForm
    template_name = 'have_form.html'
    success_url = reverse_lazy('books')

    def get_initial(self):
        initial = super().get_initial()
        # Recollim dades del llibre dels paràmetres GET
        initial['isbn'] = self.request.GET.get('isbn', '')
        initial['title'] = self.request.GET.get('title', '')
        initial['author'] = self.request.GET.get('author', '')
        initial['topic'] = self.request.GET.get('topic', '')
        return initial

    def form_valid(self, form):
        isbn = form.cleaned_data.get('isbn')
        title = form.cleaned_data.get('title')
        author = form.cleaned_data.get('author')
        topic = form.cleaned_data.get('topic')

        # Si el llibre no existeix a la nostra BD, l'afegim
        try:
            book = Book.objects.get(ISBN=isbn)
        except Book.DoesNotExist:
            # Creem un nou llibre a la base de dades
            book = Book(
                ISBN=isbn,
                title=title,
                author=author,
                topic=topic or "General",
                publish_date=timezone.now().date(),  # Data actual com a predeterminada
                base_price=10  # Preu base predeterminat
            )
            book.save()

        # Obtenim l'usuari actual i li assignem al have
        custom_user = User.objects.get(auth_user=self.request.user)

        # Comprovar si ja existeix un have per aquest usuari i llibre
        existing_have = Have.objects.filter(user=custom_user, book=book).first()

        if existing_have:
            # Actualitzar l'estat si ja existeix
            existing_have.status = form.cleaned_data['status']
            existing_have.save()
        else:
            # Crear un nou have
            have = form.save(commit=False)
            have.user = custom_user
            have.book = book
            have.save()

        return redirect(self.success_url)

def book_entry(request,ISBN):
    mybook = Book.objects.get(ISBN=ISBN)
    return  render(request,'book-entry.html', {'mybook': mybook})

def book_trade_view(request):
    return render(request, 'trade_form.html')

def book_buy_view(request):
    return  render(request, 'buy_form.html')

def wishlist_view(request):
    return render(request, 'wishlist.html')

def havelist_view(request):
    return render(request, 'havelist.html')

def trade_form(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    users = User.objects.filter(have__book=book)  # Ajusta según tu modelo "Have"

    if request.method == 'POST':
        selected_user_id = request.POST.get('selected_user')
        if selected_user_id:
            selected_user = get_object_or_404(User, id=selected_user_id)
        
            Exchange.objects.create(
                user1=request.user.custom_user,  # Usuario actual
                user2=selected_user,
                book1=book,
                book2=None,  # Si es un intercambio de un solo libro
                location=request.user.custom_user.location,
                status='proposed'
            )
            
    
            messages.success(request, f"Intercanvi confirmat amb {selected_user.name}!")
            return redirect('trade_success') 
        else:
            messages.error(request, "Has de seleccionar un usuari per confirmar l'intercanvi.")

    return render(request, 'trade_form.html', {'users': users, 'book': book})

def trade_success(request):
    return render(request, 'trade_success.html')

