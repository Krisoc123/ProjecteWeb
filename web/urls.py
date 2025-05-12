from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),  # Vista de login personalizada
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),  # Vista de registro personalizada
    path('books/', views.books, name='books'),
    path('accounts/profile/', views.profile_view, name='profile'),
    path('add-to-wishlist/', views.CreateWantView.as_view(), name='add_to_wishlist'),
    path('add-to-havelist/', views.CreateHaveView.as_view(), name='add_to_havelist'),
]