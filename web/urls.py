from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import ReviewCreateView, ReviewUpdateView, ReviewDeleteView

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
    path('book/<str:isbn>/review/new/', ReviewCreateView.as_view(), name='review-create'),
    path('review/<int:pk>/update/', ReviewUpdateView.as_view(), name='review-update'),
    path('review/<int:pk>/delete/', ReviewDeleteView.as_view(), name='review-delete'),
    path('wishlist/', views.wishlist_view ,name='wishlist'),
    path('havelist/', views.havelist_view ,name='havelist'),
    path('trade/', views.book_trade_view ,name='book-trade'),
    path('buy/', views.book_buy_view ,name='book-buy'),
    path('trade/<int:book_id>/', views.trade_form, name='trade_form'),
    path('trade/success/', views.trade_success, name='trade_success'),
]
