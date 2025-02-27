from django.db import models

class User(models.Model):
    userId = models.AutoField(primary_key=True)
    points = models.IntegerField(default=0)
    ubication = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    joined_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    ISBN = models.CharField(max_length=13, primary_key=True)  # ISBN com a identificador únic
    author = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    publish_date = models.DateField()
    base_price = models.IntegerField()  # Punts com a unitat

    def __str__(self):
        return f"{self.author} - {self.ISBN}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ressenya de {self.user.name} per {self.book.ISBN}"

class Tengo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.name} té {self.book.ISBN}"

class Quiero(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    prioritat = models.IntegerField(default=1)  # Es podria utilitzar per prioritzar books desitjats

    def __str__(self):
        return f"{self.user.name} vol {self.book.ISBN} amb prioritat {self.prioritat}"

class VendaDonacio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    points = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    ubication = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.name} ven/dona {self.book.ISBN} per {self.points} points"

class Intercanvi(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="intercanvis_fets")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="intercanvis_rebuts")
    book1 = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="book_intercanviat_per")
    book2 = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="book_rebut_com_intercanvi")
    date = models.DateTimeField(auto_now_add=True)
    ubication = models.CharField(max_length=255)

    def __str__(self):
        return f"Intercanvi entre {self.user1.name} i {self.user2.name}"
