from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import User as CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    location = forms.CharField(required=False, max_length=255)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    @transaction.atomic
    def save(self, commit=True):
        # No guardamos nada hasta que todas las validaciones hayan pasado
        # UserCreationForm ya valida las contraseñas
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'] # Asignamos el email al usuario
        
        if commit:
            user.save()
            # La señal post_save creará el CustomUser, pero podemos actualizarlo con campos adicionales
            if hasattr(user, 'custom_user'):
                custom_user = user.custom_user
                custom_user.location = self.cleaned_data.get('location', '')
                custom_user.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)