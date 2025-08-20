from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    watchlist = models.ManyToManyField(
        "Listing", 
        related_name="watched_by",  
        blank=True
    )

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class Listing(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=64)
    description = models.TextField()
    price = models.IntegerField()
    photo = models.URLField(
        blank = True,
        null=True
    )
    
    owner = models.ForeignKey(
        User, 
        on_delete = models.CASCADE, 
        related_name = "listings"
    )

    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="category"
    )    

    date = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(User, max_length=64, null=True, blank=True, on_delete=models.SET_NULL, related_name="won_listings")
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date"]
    
    def __str__(self):
        return self.name

class Bid(models.Model):
    # A bid can only be placed by one user so its a Foreignkey
    user = models.ForeignKey(
        User, 
        models.CASCADE,
        related_name = "bids"
    )

    listing = models.ForeignKey(
        Listing, 
        models.CASCADE,
        related_name = "bids" 
    )

    date = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()

    class Meta:
        ordering = ["-date"]
    
    def __str__(self):
         return f"{self.amount}"

class Comment(models.Model):
    # Only one user can make a single comment not many do the same one
    user = models.ForeignKey(
        User, 
        models.CASCADE, 
        related_name = "comments"
    )

    listing = models.ForeignKey(
        Listing, 
        models.CASCADE, 
        related_name = "comments"
    )

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.comment

    date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()

