from django.contrib import admin
from .models import User, Book, Review, Exchange, SaleDonation, Want, Have

# Register your models here.

admin.site.register(User)
admin.site.register(Book)
admin.site.register(Review)
admin.site.register(Exchange)
admin.site.register(SaleDonation)
admin.site.register(Want)
admin.site.register(Have)
