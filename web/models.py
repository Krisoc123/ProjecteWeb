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
    points = models.IntegerField(default=0)
    location = models.CharField(max_length=255, default="not specified")
    name = models.CharField(max_length=255, default="Anonymous")
    email = models.EmailField(unique=True)
    joined_date = models.DateTimeField(auto_now_add=True)

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.name} for {self.book.ISBN}"

class Have(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    points = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.user.name} sells/donates {self.book.ISBN} for {self.points} points (Status: {self.status})"

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
    book2 = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="book_received_as_exchange")
    date = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='proposed')

    def __str__(self):
        return f"Exchange between {self.user1.name} and {self.user2.name} (Status: {self.status})"