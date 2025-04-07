from django.contrib import admin
from .models import User, Book, Review, Have, Want, SaleDonation, Exchange

# Register your models here.

admin.site.register(User)
admin.site.register(Book)
admin.site.register(Review)
admin.site.register(Have)
admin.site.register(Want)
admin.site.register(SaleDonation)
admin.site.register(Exchange)
# This code registers the models with the Django admin site, allowing them to be managed through the admin interface.