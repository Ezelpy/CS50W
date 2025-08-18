from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User, Listing, Category, Bid, Comment
from . forms import ListingForm, BidForm, CommentForm

def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings,
    })

def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

@login_required
def watchlist(request):
    listings = request.user.watchlist.all() 
    return render(request, "auctions/watchlist.html", {
        "listings": listings,
    })

@login_required
def create(request):
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data          
            listing = Listing(
                name = cd["name"],
                description = cd["description"],
                price = cd["price"],
                owner = request.user,
                category = cd["category"],
                active = True,
                photo = cd["photo"],
            )
            listing.save()
            return HttpResponseRedirect(reverse("index"))

    else:
        form = ListingForm()
        return render(request, "auctions/createlisting.html", {
            "form": form
        })

def listing(request, id):
    # If user is logged in
    # User can add or remove item from the watchlist
    # User can place a bid that should be greater than the current bid
    # User can comment to the listing page and display all the other comments

    # If user is logged in and is owner
    # User should be able to close the listing
    # This makes the highest bidder win the auction

    # If the user is logged in and has won a closed auction
    # The user should be able to see that they won the auction
        try:
            listing = Listing.objects.get(id=id)
            inWatchlist = False
            if request.user.is_authenticated:
                inWatchlist = listing in request.user.watchlist.all() 

            if request.method == "POST":
                if inWatchlist:
                    request.user.watchlist.remove(listing)
                    inWatchlist = False
                else:
                    request.user.watchlist.add(listing)
                    inWatchlist = True

            bidForm = BidForm()
            commentForm = CommentForm()
            comments = Comment.objects.all()
            bids = listing.bids.all()
            bidCount = listing.bids.count()
            highestBig = bids.order_by("-amount").first()
            listing = Listing.objects.get(id=id)
        
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "bidForm": bidForm,
                "comments":comments,
                "commentForm": commentForm,
                "highestBid": highestBig,
                "bidCount": bidCount,
                "inWatchlist": inWatchlist
            })
        
        except RuntimeError:
            message = "EROR 404: listing not found"
            return render(request, "auctions/error.html", {
                "message": message,
            })
    



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    

