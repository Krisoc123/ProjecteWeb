from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib import messages
from django.db import transaction, models
from django.db.models import Avg

from django.views.decorators.http import require_POST


from .forms import CustomUserCreationForm, LoginForm, WantForm, HaveForm, ReviewForm
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
    # If user is already authenticated, redirect to home
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-login after registration
            login(request, user)
            messages.success(request, "Registration successful! You are now logged in.")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})

def login_view(request):
    # If the user is already authenticated, redirect to home
    if request.user.is_authenticated:
        return redirect('home')
        
    # If the request is a POST, user is trying to log in
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
    # If the request is a GET, show the login form
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
    exchanges_list = Exchange.objects.filter(user1=custom_user).union(Exchange.objects.filter(user2=custom_user))
    sales_list = SaleDonation.objects.filter(user1=custom_user)
    purchases_list = SaleDonation.objects.filter(user2=custom_user)
    reviews_list = Review.objects.filter(user=custom_user)
    
    context = {
        'custom_user': custom_user,
        'have_list': have_list,
        'want_list': want_list,
        'exchanges_list': exchanges_list,
        'sales_list': sales_list,
        'purchases_list': purchases_list,
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
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'editar_perfil.html', {'form': form})

def books(request):
    # Get search parameters from request
    author = request.GET.get('author', '')
    title = request.GET.get('title', '')
    topic = request.GET.get('topic', '')

    # Filter local books
    queryset = Book.objects.all()

    if author:
        queryset = queryset.filter(author__icontains=author)

    if title:
        queryset = queryset.filter(title__icontains=title)

    if topic:
        queryset = queryset.filter(topic__icontains=topic)

    # Get external books if search parameters exist
    external_books = []
    if author or title or topic:
        # Search Google Books API
        search_terms = []
        if title:
            search_terms.append(f"intitle:{title}")
        if author:
            search_terms.append(f"inauthor:{author}")
        if topic:
            search_terms.append(f"subject:{topic}")

        search_query = " ".join(search_terms).strip()

        if search_query:
            try:
                api_url = f"https://www.googleapis.com/books/v1/volumes?q={search_query}&maxResults=20"
                google_response = requests.get(api_url)

                if google_response.status_code == 200:
                    data = google_response.json()
                    for item in data.get('items', []):
                        volume_info = item.get('volumeInfo', {})

                        isbn = ''
                        for identifier in volume_info.get('industryIdentifiers', []):
                            if identifier.get('type') in ['ISBN_10', 'ISBN_13']:
                                isbn = identifier.get('identifier', '')
                                break

                        # Extract book categories if available
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
                            'topic': book_topic 
                        })
            except Exception as e:
                pass  # Silently handle API errors

    context = {
        'books': queryset,
        'external_books': external_books
    }

    return render(request, 'books.html', context)

def trending_view(request):
    """
    View to show the most popular books (with more exchanges and sales).
    Counts both exchanges and sales/donations, and shows books ordered
    by total number of transactions.
    """
    from django.db.models import Count, Q, F
    from itertools import chain
    
    # Books involved in exchanges (either as book1 or book2)
    # Include both 'completed' and 'accepted' exchanges
    exchanged_books = Book.objects.annotate(
        exchange_count=Count('book_exchanged_by', filter=Q(book_exchanged_by__status__in=['completed', 'accepted']), distinct=True) + 
                      Count('book_received_as_exchange', filter=Q(book_received_as_exchange__status__in=['completed', 'accepted']), distinct=True)
    ).filter(exchange_count__gt=0).order_by('-exchange_count')
    
    # Books involved in sales/donations
    sold_books = Book.objects.annotate(
        sale_count=Count('saledonation', filter=Q(saledonation__status__in=['completed', 'accepted']), distinct=True)
    ).filter(sale_count__gt=0).order_by('-sale_count')
    
    # Combine both querysets and sort by total transactions
    from itertools import chain
    all_books = list(chain(exchanged_books, sold_books))
    
    # Remove duplicates and sort by total transaction count
    unique_books = {}
    for book in all_books:
        if book.ISBN not in unique_books:
            # Add counts if the book has both exchanges and sales
            exchange_count = getattr(book, 'exchange_count', 0)
            sale_count = getattr(book, 'sale_count', 0)
            book.total_count = exchange_count + sale_count
            unique_books[book.ISBN] = book
    
    # Sort by total count
    trending_books = sorted(unique_books.values(), key=lambda x: x.total_count, reverse=True)
    
    # Limit to top 10 books
    trending_books = trending_books[:10]
    
    # If no trending books found, get some books anyway
    if not trending_books:
        trending_books = Book.objects.annotate(
            exchange_count=Count('book_exchanged_by', filter=Q(book_exchanged_by__status__in=['completed', 'accepted']), distinct=True) + 
                        Count('book_received_as_exchange', filter=Q(book_received_as_exchange__status__in=['completed', 'accepted']), distinct=True)
        ).order_by('-exchange_count')[:10]
        
        # Add a total_count attribute for consistency
        for book in trending_books:
            book.total_count = getattr(book, 'exchange_count', 0)
    
    return render(request, 'trending.html', {'trending_books': trending_books})

class CreateWantView(LoginRequiredMixin, CreateView):
    model = Want
    form_class = WantForm
    template_name = 'want_form.html'
    success_url = reverse_lazy('books')

    def get_initial(self):
        initial = super().get_initial()
        # Get book data from GET parameters
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

        # If book doesn't exist in our DB, add it
        try:
            book = Book.objects.get(ISBN=isbn)
        except Book.DoesNotExist:
            # Create new book in database
            book = Book(
                ISBN=isbn,
                title=title,
                author=author,
                topic=topic or "General",
                publish_date=timezone.now().date(),
                base_price=10
            )
            book.save()

        # Get current user and assign to want
        custom_user = User.objects.get(auth_user=self.request.user)

        # Check if want already exists for this user and book
        existing_want = Want.objects.filter(user=custom_user, book=book).first()

        if existing_want:
            # Update priority if already exists
            existing_want.priority = form.cleaned_data['priority']
            existing_want.save()
        else:
            # Create new want
            want = form.save(commit=False)
            want.user = custom_user
            want.book = book
            want.save()

        return redirect(self.success_url)

class CreateHaveView(LoginRequiredMixin, CreateView):
    model = Have
    form_class = HaveForm
    template_name = 'have_form.html'
    success_url = reverse_lazy('books')

    def get_initial(self):
        initial = super().get_initial()
        # Get book data from GET parameters
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

        # If book doesn't exist in our DB, add it
        try:
            book = Book.objects.get(ISBN=isbn)
        except Book.DoesNotExist:
            # Create new book in database
            book = Book(
                ISBN=isbn,
                title=title,
                author=author,
                topic=topic or "General",
                publish_date=timezone.now().date(),
                base_price=10
            )
            book.save()

        # Get current user and assign to have
        custom_user = User.objects.get(auth_user=self.request.user)

        # Check if have already exists for this user and book
        existing_have = Have.objects.filter(user=custom_user, book=book).first()

        if existing_have:
            # Update status if already exists
            existing_have.status = form.cleaned_data['status']
            existing_have.save()
        else:
            # Create new have
            have = form.save(commit=False)
            have.user = custom_user
            have.book = book
            have.save()

        return redirect(self.success_url)


def book_entry(request, ISBN):
    try:
        # Fetch the book from the local database
        mybook = Book.objects.get(ISBN=ISBN)
        is_local = True
        reviews = Review.objects.filter(book=mybook).order_by('-date')

    except Book.DoesNotExist:
        # If the book is not found in the local database, try to fetch it from an external API
        mybook = None
        is_local = False
        reviews = []

        try:
            api_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{ISBN}"
            response = requests.get(api_url)

            if response.status_code == 200:
                data = response.json()
                if data.get('items'):

                    item = data['items'][0]
                    volume_info = item.get('volumeInfo', {})

                    # Create a book object with the fetched data
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
            pass  # Handle API errors silently

    if not mybook:
        messages.error(request, "Book not found in our database or external sources.")
        return redirect('books')
    avg_rating = None
    book_availability = None
    book_condition = 'used'  # default
    
    if is_local and reviews.exists():
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    # Get availability info for schema.org markup
    book_sellers = []
    transaction_count = 0
    if is_local:
        from .models import Have, SaleDonation, Exchange
        from collections import Counter
        
        # Get all Have instances for this book
        have_instances = Have.objects.filter(book=mybook).select_related('user')
        available_copies = have_instances.count()
        
        # Get transaction history for popularity metrics
        sales_count = SaleDonation.objects.filter(book=mybook).count()
        exchanges_count = Exchange.objects.filter(book1=mybook).count() + Exchange.objects.filter(book2=mybook).count()
        transaction_count = sales_count + exchanges_count
        
        if available_copies > 0:
            book_availability = 'http://schema.org/InStock'
            # Get the most common condition
            conditions = have_instances.values_list('status', flat=True)
            if conditions:
                most_common = Counter(conditions).most_common(1)
                book_condition = most_common[0][0] if most_common else 'used'
            
            # Get sellers info for detailed markup
            for have in have_instances[:3]:  # Limit to 3 for performance
                book_sellers.append({
                    'user': have.user,
                    'status': have.status,
                    'points': have.points,
                    'date_added': have.user.joined_date 
                })
        else:
            book_availability = 'http://schema.org/OutOfStock'
    
    return render(request, 'book-entry.html', {
        'mybook': mybook,
        'is_local': is_local,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'book_availability': book_availability,
        'book_condition': book_condition,
        'book_sellers': book_sellers,
        'available_copies': len(book_sellers) if book_sellers else 0,
        'transaction_count': transaction_count
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
    try:
        book = Book.objects.get(ISBN=ISBN)
    except Book.DoesNotExist:
        messages.error(request, f"Book with ISBN {ISBN} not found.")
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
    
    context = {
        'users': users,
        'book': book,
        'selected_user_id': None,
        'user_books': [],
        'user_tokens': current_user.points
    }
    
    if request.method == 'POST':
        selected_user_id = request.POST.get('selected_user')

        
        if selected_user_id:
            
            selected_user = get_object_or_404(User, userId=selected_user_id)
                            
            context['selected_user_id'] = selected_user_id
            context['selected_user'] = selected_user
            
            # Discount points from buyer
            buyer = current_user
            if buyer.points >= book.base_price:
                buyer.points -= book.base_price
                buyer.save()

                # Transfer points to the offering user
                if selected_user != buyer:
                    selected_user.points += book.base_price
                    selected_user.save()
                
                # Seller gets the points, doesn't have book anymore
                Have.objects.filter(user=selected_user, book=book).delete()

                # Create a SaleDonation object
                sale = SaleDonation(
                    user1=selected_user,
                    user2=buyer,
                    book=book,
                    points=book.base_price,
                    status='pending'
                )
                sale.save()

                messages.success(request, "Book acquired successfully.")
                return render(request, 'sale_success.html', context)
            else:
                messages.error(request, "You don't have enough points to acquire this book.")
                return redirect('book-entry', ISBN=ISBN)
        
        else:
            messages.error(request, "No user selected.")
            
            
    
    
    return render(request, 'buy_form.html', context)


def get_book(request, offer_id):
    offer = get_object_or_404(SaleDonation, id=offer_id)
    buyer = request.user

    if offer.status != 'pending':
        messages.error(request, "This offer has already been processed.")
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

        messages.success(request, "Book acquired successfully.")
    else:
        messages.error(request, "You don't have enough points to acquire this book.")

    return redirect('home')


def wishlist_view(request):
    return render(request, 'wishlist.html')

def havelist_view(request):
    return render(request, 'havelist.html')



# View to create a review
class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
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
                context['book'] = {'ISBN': isbn, 'title': 'Unknown Book'}

        context['action'] = 'Create'
        return context

    def get_success_url(self):
        return reverse_lazy('book-entry', kwargs={'ISBN': self.kwargs['isbn']})


# View to update a review
class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    form_class = ReviewForm
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


# View to delete a review
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

    context = {
        'users': users,
        'book': book,
        'selected_user_id': None,
        'user_books': []
    }
    
    if request.method == 'POST':
        selected_user_id = request.POST.get('selected_user')
        selected_book_id = request.POST.get('selected_book')
        
        if selected_user_id and not selected_book_id:
            try:
                selected_user = get_object_or_404(User, userId=selected_user_id)
                
                user_have_objects = Have.objects.filter(user=selected_user).select_related('book')
                user_books = [have.book for have in user_have_objects]
                
                if not user_books:
                    messages.warning(request, f"{selected_user.name} has no books available for exchange.")
                
                context['selected_user_id'] = selected_user_id
                context['user_books'] = user_books
                context['selected_user'] = selected_user
                
                return render(request, 'trade_form.html', context)
            
            except Exception as e:
                messages.error(request, f"Error loading user books: {str(e)}")
        
        elif selected_user_id and selected_book_id:
            try:
                selected_user = get_object_or_404(User, userId=selected_user_id)
                
                try:
                    selected_book = Book.objects.get(ISBN=selected_book_id)
                    
                    with transaction.atomic():
                        # Create the exchange record
                        exchange = Exchange(
                            user1=current_user,
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
                    messages.error(request, f"Book with ISBN {selected_book_id} not found.")
                    return redirect('book-trade')
                
                # Set success message for display
                messages.success(request, f"Exchange confirmed with {selected_user.name}! Your book '{book.title}' for '{selected_book.title}'")
                return redirect('trade_success_page')
            except Exception as e:
                messages.error(request, f"Error processing exchange: {str(e)}")
        else:
            messages.error(request, "You must select a user and a book to confirm the exchange.")

    return render(request, 'trade_form.html', context)

def trade_success(request):
    return render(request, 'trade_success.html')

