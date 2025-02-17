from django.shortcuts import render
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect

# Create your views here.

def home(request):
    return render(request, 'home.html')

def logout_view(request):
    auth_logout(request)
    return redirect('home')
