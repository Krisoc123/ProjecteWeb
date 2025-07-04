from django.db import models
from django.contrib.auth.models import User as AuthUser
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=AuthUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        User.objects.create(
            auth_user=instance,
            name=instance.username,
            email=instance.email
        )

@receiver(post_save, sender=AuthUser)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'custom_user'):
        instance.custom_user.save()
        
class User(models.Model):
    userId = models.AutoField(primary_key=True)
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, related_name='custom_user', null=True)
    points = models.IntegerField(default=50)
    location = models.CharField(max_length=255, default="not specified")
    name = models.CharField(max_length=255, default="Anonymous")
    email = models.EmailField(unique=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name

class Book(models.Model):
    ISBN = models.CharField(max_length=13, primary_key=True)  # ISBN as unique identifier
    title = models.CharField(max_length=255, default="Unknown")
    author = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    publish_date = models.DateField()
    base_price = models.IntegerField()  # Points as unit

    def __str__(self):
        return f"{self.author} - {self.ISBN}"

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES, default=3)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.name} for {self.book.ISBN}"

class Have(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('damaged', 'Damaged')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='used')
    points = models.IntegerField(default=99)  # Points as unit
    
    def __str__(self):
        return f"{self.user.name} has {self.book.ISBN}"

class Want(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    priority = models.IntegerField(default=1)  # Can be used to prioritize desired books

    def __str__(self):
        return f"{self.user.name} wants {self.book.ISBN} with priority {self.priority}"

class SaleDonation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sales_made", null=True)
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchases_made", null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    points = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.user1.name} sells/donates {self.book.ISBN} to {self.user2.name} for {self.points} points (Status: {self.status})"
    
    
class Exchange(models.Model):
    STATUS_CHOICES = [
        ('proposed', 'Proposed'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exchanges_made")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exchanges_received")
    book1 = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="book_exchanged_by")
    book2 = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="book_received_as_exchange", null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='proposed')

    def __str__(self):
        return f"Exchange between {self.user1.name} and {self.user2.name} (Status: {self.status})"

