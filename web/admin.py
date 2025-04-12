from django.contrib import admin
from .models import User, Book, Review, Have, Want, SaleDonation, Exchange

# Configuració personalitzada per User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'points', 'location', 'joined_date')
    search_fields = ('name', 'email', 'location')
    list_filter = ('joined_date',)
    readonly_fields = ('joined_date',)
    fieldsets = (
        ('Informació Personal', {
            'fields': ('auth_user', 'name', 'email')
        }),
        ('Informació del Sistema', {
            'fields': ('points', 'location', 'joined_date')
        }),
    )

# Configuració per al model Book
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('ISBN', 'title', 'author', 'topic', 'base_price')
    search_fields = ('ISBN', 'title', 'author', 'topic')
    list_filter = ('topic',)

# Configuració per al model Review
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'book')
    search_fields = ('book__title',)

# Configuració per al model Have
@admin.register(Have)
class HaveAdmin(admin.ModelAdmin):
    list_display = ('user', 'book')
    search_fields = ('book__title',)

# Configuració per al model Want
@admin.register(Want)
class WantAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'priority')
    search_fields = ('book__title',)
    list_filter = ('priority',)

# Configuració per al model SaleDonation
@admin.register(SaleDonation)
class SaleDonationAdmin(admin.ModelAdmin):
    list_display = ('book', 'status')
    search_fields = ('book__title',)
    list_filter = ('status',)

# Configuració per al model Exchange
@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('book1', 'book2', 'location', 'status')
    search_fields = ('book1__title', 'book2__title', 'location')
    list_filter = ('status',)