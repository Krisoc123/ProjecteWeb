from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('books/', views.books, name='books'),
    path('accounts/profile/', views.profile_view, name='profile'),
    path('books/<ISBN>/', views.book_entry ,name='book-entry'),
] 