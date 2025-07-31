from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    watchlist = models.ManyToManyField(
        "Listings", 
        related_name="watched_by",  
        blank=True
    )

class Categories(models.Model):
    name = models.CharField(max_length=64)

class Listings(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    price = models.IntegerField()
    photo = models.ImageField(
        upload_to="listingPhotos",
        null=True,
        blank=True
    )
    
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="listings"
    )

    category = models.ForeignKey(
        Categories, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )    

    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

class Bids(models.Model):
    # A bid can only be placed by one user so its a Foreignkey
    user = models.ForeignKey(
        User, 
        models.CASCADE,
        related_name="bids"
    )

    listing = models.ForeignKey(
        Listings, 
        models.CASCADE, 
        related_name="bids"
    )

    date = models.DateTimeField(auto_now_add=True)
    amount = models.PositiveBigIntegerField()

class Comments(models.Model):
    # Only one user can make a single comment not many do the same one
    user = models.ForeignKey(
        User, 
        models.CASCADE, 
        related_name="comments"
    )

    listing = models.ForeignKey(
        Listings, 
        models.CASCADE, 
        related_name="comments"
    )

    date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()

