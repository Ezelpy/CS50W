from django.contrib import admin

from .models import Bids, Comments, Listings, Categories

# Register your models here.

admin.site.register(Bids)
admin.site.register(Comments)
admin.site.register(Listings)
admin.site.register(Categories)