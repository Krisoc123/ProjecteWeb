from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib import messages
from django.db import transaction, models


from django.views.decorators.http import require_POST


from .forms import CustomUserCreationForm, LoginForm, WantForm, HaveForm
from django.contrib.auth.decorators import login_required
from .models import User, Book, Review, Have, Want, SaleDonation, Exchange
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from .forms import UserProfileForm

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
    if request.method == 'POST' and 'profile_picture' in request.FILES:
        custom_user.profile_picture = request.FILES['profile_picture']
        custom_user.save()
        return redirect('profile')

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=custom_user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=custom_user)

    # Now use custom_user for your queries
    have_list = Have.objects.filter(user=custom_user)
    want_list = Want.objects.filter(user=custom_user)
    exchanges_list = Exchange.objects.filter(user1=custom_user)
    sales_list = SaleDonation.objects.filter(user=custom_user)
    reviews_list = Review.objects.filter(user=custom_user)
    
    context = {
        'custom_user': custom_user,  # Canviem el nom de la variable per evitar conflicte
        'have_list': have_list,
        'want_list': want_list,
        'exchanges_list': exchanges_list,
        'sales_list': sales_list,
        'reviews_list': reviews_list,
    }
    
    return render(request, 'profile.html', context)

@require_POST
@login_required
def delete_book_from_list(request):
    isbn = request.POST.get('isbn')
    list_type = request.POST.get('list_type')
    custom_user = User.objects.get(auth_user=request.user)

    if list_type == 'have':
        item = get_object_or_404(Have, user=custom_user, book__ISBN=isbn)
    elif list_type == 'want':
        item = get_object_or_404(Want, user=custom_user, book__ISBN=isbn)
    else:
        messages.error(request, "Tipo de lista no válido.")
        return redirect('profile')

    item.delete()
    messages.success(request, "Libro eliminado correctamente.")
    return redirect('profile')


@login_required
def editar_perfil(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # O como se llame tu vista de perfil
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'editar_perfil.html', {'form': form})

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
        # Usamos icontains para hacer la búsqueda más flexible
        queryset = queryset.filter(topic__icontains=topic)

    # Obtenim llibres d'APIs externes si hi ha paràmetres de cerca
    external_books = []
    if author or title or topic:
        # Cerca a Google Books API
        search_terms = []
        if title:
            search_terms.append(f"intitle:{title}")  # Mejorado para búsquedas más precisas
        if author:
            search_terms.append(f"inauthor:{author}")
        if topic:
            # Aseguramos que el tema se busca correctamente en Google Books
            search_terms.append(f"subject:{topic}")

        search_query = " ".join(search_terms).strip()
        print(f"Cercant amb el terme: '{search_query}'")  # Logging

        if search_query:
            try:
                api_url = f"https://www.googleapis.com/books/v1/volumes?q={search_query}&maxResults=20"
                print(f"Cridant API: {api_url}")  # Logging
                google_response = requests.get(api_url)
                print(f"Codi de resposta: {google_response.status_code}")  # Logging

                if google_response.status_code == 200:
                    data = google_response.json()
                    print(f"Resultats obtinguts: {len(data.get('items', []))}")  # Logging
                    for item in data.get('items', []):
                        volume_info = item.get('volumeInfo', {})

                        isbn = ''
                        for identifier in volume_info.get('industryIdentifiers', []):
                            if identifier.get('type') in ['ISBN_10', 'ISBN_13']:
                                isbn = identifier.get('identifier', '')
                                break

                        # Extraemos categorías del libro si están disponibles
                        categories = volume_info.get('categories', [])
                        book_topic = categories[0] if categories else topic if topic else "General"

                        external_books.append({
                            'title': volume_info.get('title', 'Unknown Title'),
                            'author': ', '.join(volume_info.get('authors', ['Unknown Author'])),
                            'description': volume_info.get('description', ''),
                            'thumbnail_url': volume_info.get('imageLinks', {}).get('thumbnail', ''),
                            'ISBN': isbn,
                            'external_link': volume_info.get('infoLink', ''),
                            'source': 'Google Books',
                            'topic': book_topic  # Añadimos la categoría del libro
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


def book_entry(request, ISBN):
    try:
        # Primero intenta encontrar el libro en la base de datos local
        mybook = Book.objects.get(ISBN=ISBN)
        is_local = True

        # Obtener las reviews del libro si es local
        reviews = Review.objects.filter(book=mybook).order_by('-date')

    except Book.DoesNotExist:
        # Si no existe localmente, buscar en fuentes externas (Google Books)
        mybook = None
        is_local = False
        reviews = []  # No hay reviews para libros externos

        try:
            api_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{ISBN}"
            response = requests.get(api_url)

            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    # Tomar el primer resultado que coincida con el ISBN
                    item = data['items'][0]
                    volume_info = item.get('volumeInfo', {})

                    # Crear un "libro virtual" con los mismos campos que el modelo Book
                    mybook = {
                        'ISBN': ISBN,
                        'title': volume_info.get('title', 'Unknown Title'),
                        'author': ', '.join(volume_info.get('authors', ['Unknown Author'])),
                        'topic': volume_info.get('categories', ['General'])[0] if volume_info.get('categories') else 'General',
                        'publish_date': volume_info.get('publishedDate', ''),
                        'description': volume_info.get('description', ''),
                        'thumbnail_url': volume_info.get('imageLinks', {}).get('thumbnail', ''),
                        'external_link': volume_info.get('infoLink', ''),
                        'source': 'Google Books'
                    }
        except Exception as e:
            print(f"Error fetching book from API: {e}")

    if not mybook:
        messages.error(request, "Book not found in our database or external sources.")
        return redirect('books')

    # Pasar a la plantilla tanto el libro como un indicador de si es local o externo, y las reviews
    return render(request, 'book-entry.html', {
        'mybook': mybook,
        'is_local': is_local,
        'reviews': reviews
    })

def book_trade_view(request):
    """Show a list of books available for trading."""
    # Get the current user's custom_user
    if hasattr(request.user, 'custom_user'):
        current_user = request.user.custom_user
    else:
        # If the custom_user doesn't exist and the user is authenticated, create it
        if request.user.is_authenticated:
            current_user, created = User.objects.get_or_create(
                auth_user=request.user,
                defaults={
                    'name': request.user.username,
                    'email': request.user.email
                }
            )
        else:
            current_user = None
    
    # Get books that have at least one owner (excluding the current user)
    available_books = []
    
    # If user is logged in, we can exclude their books
    if current_user:
        # Find books that other users have
        have_objects = Have.objects.exclude(user=current_user).select_related('book', 'user')
        # Group by book to get books with at least one owner
        book_owners = {}
        for have in have_objects:
            if have.book not in book_owners:
                book_owners[have.book] = []
            book_owners[have.book].append(have.user)
        
        # Convert to list of books with owner count
        for book, owners in book_owners.items():
            available_books.append({
                'book': book,
                'owner_count': len(owners)
            })
    else:
        # For non-logged in users, show all books that have owners
        have_objects = Have.objects.select_related('book').values('book').annotate(owner_count=models.Count('user'))
        for item in have_objects:
            book = Book.objects.get(ISBN=item['book'])
            available_books.append({
                'book': book,
                'owner_count': item['owner_count']
            })
    
    # Sort by owner count (most popular first)
    available_books.sort(key=lambda x: x['owner_count'], reverse=True)
    
    # Render the trade book list template
    return render(request, 'trade_book_list.html', {
        'available_books': available_books
    })

def sale_detail(request, ISBN):
    mybook = get_object_or_404(Book, ISBN=ISBN)
    sale_donations = SaleDonation.objects.filter(book=mybook)
    user_tokens = User.objects.first().points

    context = {
        'mybook': mybook,
        'sale_donations': sale_donations,
        'user_tokens': user_tokens,
    }
    return render(request, 'buy_form.html', context)


def get_book(request, offer_id):
    offer = get_object_or_404(SaleDonation, id=offer_id)
    buyer = request.user

    if offer.status != 'pending':
        messages.error(request, "Esta oferta ya ha sido gestionada.")
        return redirect('home')

    if buyer.points >= offer.points:
        buyer.points -= offer.points
        buyer.save()

        # Transfer points to the offering user
        if offer.user != buyer:
            offer.user.points += offer.points
            offer.user.save()

        offer.status = 'completed'
        offer.save()

        messages.success(request, "Has adquirido el libro correctamente.")
    else:
        messages.error(request, "No tienes suficientes puntos para adquirir este libro.")

    return redirect('home')


def wishlist_view(request):
    return render(request, 'wishlist.html')

def havelist_view(request):
    return render(request, 'havelist.html')



# Vista para crear una review
class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    fields = ['text']
    template_name = 'review_form.html'

    def form_valid(self, form):
        # Get the custom User instance linked to the authenticated user
        custom_user = User.objects.get(auth_user=self.request.user)
        form.instance.user = custom_user

        # Verify if the book exists in the local database
        isbn = self.kwargs['isbn']
        try:
            book = Book.objects.get(ISBN=isbn)
            form.instance.book = book
            return super().form_valid(form)
        except Book.DoesNotExist:
            # If the book doesn't exist locally, show an error message
            messages.error(self.request, "You can only review books that exist in our local database.")
            return redirect('book-entry', ISBN=isbn)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        isbn = self.kwargs['isbn']
        try:
            context['book'] = Book.objects.get(ISBN=isbn)
        except Book.DoesNotExist:
            # Try to get book information from API
            try:
                api_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
                response = requests.get(api_url)

                if response.status_code == 200:
                    data = response.json()
                    if data.get('items'):
                        # Take the first result that matches the ISBN
                        item = data['items'][0]
                        volume_info = item.get('volumeInfo', {})

                        # Create a "virtual book"
                        context['book'] = {
                            'ISBN': isbn,
                            'title': volume_info.get('title', 'Unknown Title'),
                        }
            except Exception as e:
                print(f"Error fetching book from API: {e}")
                context['book'] = {'ISBN': isbn, 'title': 'Unknown Book'}

        context['action'] = 'Create'
        return context

    def get_success_url(self):
        return reverse_lazy('book-entry', kwargs={'ISBN': self.kwargs['isbn']})


# Vista para actualizar una review
class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    fields = ['text']
    template_name = 'review_form.html'

    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user.auth_user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = self.get_object().book
        context['action'] = 'Update'
        return context

    def get_success_url(self):
        return reverse_lazy('book-entry', kwargs={'ISBN': self.get_object().book.ISBN})


# Vista para eliminar una review
class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = 'review_confirm_delete.html'

    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user.auth_user

    def get_success_url(self):
        return reverse_lazy('book-entry', kwargs={'ISBN': self.get_object().book.ISBN})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = self.get_object().book
        return context

def trade_form(request, book_id):
    try:
        book = Book.objects.get(ISBN=book_id)
    except Book.DoesNotExist:
        messages.error(request, f"Book with ISBN {book_id} not found.")
        return redirect('book-trade')
    
    if hasattr(request.user, 'custom_user'):
        current_user = request.user.custom_user
    else:
        current_user, created = User.objects.get_or_create(
            auth_user=request.user,
            defaults={
                'name': request.user.username,
                'email': request.user.email
            }
        )
    
    have_objects = Have.objects.filter(book=book).exclude(user=current_user).select_related('user')
    
    unique_users = {}
    for have in have_objects:
        if have.user.userId not in unique_users:
            unique_users[have.user.userId] = have.user
    
    users = list(unique_users.values())
    
    all_have_objects = Have.objects.filter(book=book).select_related('user')
    print(f"[DEBUG] Total Have objects for this book: {all_have_objects.count()}")
    for have in all_have_objects:
        print(f"[DEBUG] Have object: {have.user.name} (ID: {have.user.userId}) (is current user? {have.user.userId == current_user.userId})")

    context = {
        'users': users,
        'book': book,
        'selected_user_id': None,
        'user_books': []
    }
    
    if request.method == 'POST':
        selected_user_id = request.POST.get('selected_user')
        selected_book_id = request.POST.get('selected_book')
        
        print(f"[DEBUG] Selected user ID: {selected_user_id}, Selected book ID: {selected_book_id}")
        
        if selected_user_id and not selected_book_id:
            try:
                selected_user = get_object_or_404(User, userId=selected_user_id)
                print(f"[DEBUG] Found selected user: {selected_user.name}")
                
                user_have_objects = Have.objects.filter(user=selected_user).select_related('book')
                user_books = [have.book for have in user_have_objects]
                
                if not user_books:
                    messages.warning(request, f"{selected_user.name} no té llibres disponibles per intercanviar.")
                
                context['selected_user_id'] = selected_user_id
                context['user_books'] = user_books
                context['selected_user'] = selected_user
                
                return render(request, 'trade_form.html', context)
            
            except Exception as e:
                print(f"[DEBUG] Error loading user books: {str(e)}")
                messages.error(request, f"Error en carregar els llibres de l'usuari: {str(e)}")
        
        elif selected_user_id and selected_book_id:
            try:
                selected_user = get_object_or_404(User, userId=selected_user_id)
                print(f"[DEBUG] Selected book ID: '{selected_book_id}'")
                
                try:
                    selected_book = Book.objects.get(ISBN=selected_book_id)
                    print(f"[DEBUG] Found selected book: {selected_book.title}")
                    
                    with transaction.atomic():
                        # Create the exchange record
                        exchange = Exchange(
                            user1=current_user,  # Current user
                            user2=selected_user,
                            book1=book,
                            book2=selected_book,
                            location=current_user.location,
                            status='accepted'  
                        )
                        exchange.save()
                        
                        user1_have = Have.objects.filter(user=current_user, book=book).first()
                        if user1_have:
                            user1_status = user1_have.status
                            user1_points = user1_have.points
                        else:
                            user1_status = 'used'
                            user1_points = 10
                            
                        user2_have = Have.objects.filter(user=selected_user, book=selected_book).first()
                        if user2_have:
                            user2_status = user2_have.status
                            user2_points = user2_have.points
                        else:
                            user2_status = 'used'
                            user2_points = 10
                            
                        # First, delete the original Have records
                        Have.objects.filter(user=current_user, book=book).delete()
                        Have.objects.filter(user=selected_user, book=selected_book).delete()
                        
                        # Then create new Have records with swapped books
                        # User1 now has User2's book
                        Have.objects.create(
                            user=current_user,
                            book=selected_book,
                            status=user2_status,
                            points=user2_points
                        )
                        
                        # User2 now has User1's book
                        Have.objects.create(
                            user=selected_user,
                            book=book,
                            status=user1_status,
                            points=user1_points
                        )
                except Book.DoesNotExist:
                    print(f"[DEBUG] Book with ISBN {selected_book_id} not found")
                    messages.error(request, f"Book with ISBN {selected_book_id} not found.")
                    return redirect('book-trade')
                
                # Set success message for display
                messages.success(request, f"Intercanvi confirmat amb {selected_user.name}! El teu llibre '{book.title}' per '{selected_book.title}'")
                return redirect('trade_success_page')
            except Exception as e:
                print(f"[DEBUG] Error processing exchange: {str(e)}")
                messages.error(request, f"Error en processar l'intercanvi: {str(e)}")
        else:
            messages.error(request, "Has de seleccionar un usuari i un llibre per confirmar l'intercanvi.")

    return render(request, 'trade_form.html', context)

def trade_success(request):
    return render(request, 'trade_success.html')

