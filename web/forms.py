from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db import transaction
from .models import User as CustomUser, Want, Book, Have

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    location = forms.CharField(required=False, max_length=255)
    """ class Meta: is used to define the model and fields for the form """
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

class WantForm(forms.ModelForm):
    priority = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Priority (1-5)'}),
        help_text='Set the priority of this book (1=lowest, 5=highest)'
    )
    
    # Hidden fields for book data
    isbn = forms.CharField(widget=forms.HiddenInput(), required=False)
    title = forms.CharField(widget=forms.HiddenInput(), required=False)
    author = forms.CharField(widget=forms.HiddenInput(), required=False)
    topic = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Want
        fields = ['priority']
        
        

class HaveForm(forms.ModelForm):
    class Meta:
        model = Have
        fields = ['status', 'isbn', 'title', 'author', 'topic']
    
    status = forms.ChoiceField(
        choices=Have.STATUS_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Selecciona l'estat del llibre"
    )
    
    # Camps ocults
    isbn = forms.CharField(widget=forms.HiddenInput(), required=False)
    title = forms.CharField(widget=forms.HiddenInput(), required=False)
    author = forms.CharField(widget=forms.HiddenInput(), required=False)
    topic = forms.CharField(widget=forms.HiddenInput(), required=False)