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
            highestBid = listing.price
            bidCount = listing.bids.count()
            isActive = listing.active

            isWinner, inWatchlist, isOwner, isCurrentBid, currentWinner = checkUserPrivileges(
                request, isActive, listing
            )

            if request.method == "POST":
                # If user wants to edit watchlist status
                if request.POST.get('watchlist'):
                    inWatchlist = modifyWatchlist(request, listing)

                # If user wants to place a bid
                elif request.POST.get('bid'):
                    form = BidForm(request.POST)

                    if form.is_valid():
                        highestBid, bidCount = bidListing(request, form, listing, highestBid, bidCount)
                    else: raise ValueError("Bid should be higher that previous bid")

                # If user wants to close the auction
                elif request.POST.get('close'):
                    isActive = closeListing(listing, currentWinner)

                # If user wants to add a comment
                elif request.POST.get('comment'):
                    form = CommentForm(request.POST)
                    addNewComment(request, listing, form)

            # In any case, return to listing
            bidForm = BidForm()
            commentForm = CommentForm()
            comments = listing.comments.all()
            
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "bidForm": bidForm,
                "comments":comments,
                "commentForm": commentForm,
                "highestBid": highestBid,
                "bidCount": bidCount,
                "inWatchlist": inWatchlist,
                "isActive": isActive,
                "isOwner": isOwner,
                "isWinner": isWinner,
                "isCurrentBid": isCurrentBid,
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
    

# Helper functions
# LISTING PAGE

# FUNCTION
# NAME:        checkUserPrivileges
# DESCRIPTION: Function will check user privileges and update the variables
# ARGUMENTS:   It needs the request, a boolean stating if the auction is 
#              active, and the listing
# OUTPUT:      It returns a boolean stating if the current user is the winner 
#              of the auction, if the listing is in the watchlist, if the user
#              is the owner of the listing, if the user is the current highest
#              bidder, and the highest bidder
def checkUserPrivileges(request, isActive, listing):
    currentWinner = Bid.objects.all().order_by("-amount").first().user
    inWatchlist = False
    isOwner = False
    isWinner = False
    isCurrentBid = False

    if not isActive:
        isWinner = listing.winner == request.user
            
    if request.user.is_authenticated:
        inWatchlist = listing in request.user.watchlist.all()
        isOwner = request.user == listing.owner
        isCurrentBid = request.user == currentWinner
    
    return isWinner, inWatchlist, isOwner, isCurrentBid, currentWinner

# FUNCTION
# NAME:        modifyWatchlist
# DESCRIPTION: Function will modify the watchlist status of a listing
# ARGUMENTS:   It needs the request and a listing
# OUTPUT:      It returns a boolean stating if the current listing is 
#              in the watchlist
def modifyWatchlist(request, listing):
    if inWatchlist:
        request.user.watchlist.remove(listing)
        inWatchlist = False
    else:
        request.user.watchlist.add(listing)
        inWatchlist = True
    return inWatchlist

# FUNCTION
# NAME:        bidListing
# DESCRIPTION: Function will add new bid to the listing
# ARGUMENTS:   It needs the request, the listing, bid, and current number 
#              of bids
# OUTPUT:      It returns the new highest bid and the updated number of bids
def bidListing(request, form, listing, highestBid, bidCount):
    bid = form.cleaned_data["bid"]
    if bid > highestBid:
        newBid = Bid.objects.create(
            user=request.user,
            listing=listing,
            amount=bid
        )
        listing.price = bid
        highestBid = bid
        bidCount += 1
        listing.save()
    return highestBid, bidCount

    
    

# FUNCTION
# NAME:        closeListing
# DESCRIPTION: Function will close the listing and set the winner as the 
#              highest bidder.
# ARGUMENTS:   It needs the listing and the user that is currently winning the
#              bid
# OUTPUT:      It returns a boolean stating the listing is not active
def closeListing(listing, currentWinner):
    listing.winner = currentWinner
    listing.active = False
    isActive = False
    listing.save()
    return isActive

# FUNCTION
# NAME:        addNewComment
# DESCRIPTION: Function will add a new comment if the form is valid
# ARGUMENTS:   It needs the request, the listing and the comment form
# OUTPUT:      None
def addNewComment(request, listing, form):
    if form.is_valid():
        comment = form.cleaned_data["comment"]
        newComment = Comment.objects.create(
            user=request.user,
            listing=listing,
            comment=comment,
        )