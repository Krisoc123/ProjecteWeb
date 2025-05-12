from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('books/', views.books, name='books'),
    path('accounts/profile/', views.profile_view, name='profile'),
    path('add-to-wishlist/', views.CreateWantView.as_view(), name='add_to_wishlist'),
    path('add-to-havelist/', views.CreateHaveView.as_view(), name='add_to_havelist'),

    path('trending/', views.trending_view, name='trending'),
    path('books/entry/<ISBN>/', views.book_entry ,name='book-entry'),
    path('wishlist/', views.wishlist_view ,name='wishlist'),
    path('shelve/', views.shelve_view ,name='shelve'),
    path('book-trade/<ISBN>', views.book_trade_view ,name='book-trade'),
    path('books/buy/', views.book_buy_view ,name='book-buy'),
]
