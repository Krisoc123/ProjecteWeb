from django.contrib import admin
from .models import User, Book, Review, Tengo, Quiero, VendaDonacio, Intercanvi

# Register your models here.

admin.site.register(User)
admin.site.register(Book)
admin.site.register(Review)
admin.site.register(Tengo)
admin.site.register(Quiero)
admin.site.register(VendaDonacio)
admin.site.register(Intercanvi)

