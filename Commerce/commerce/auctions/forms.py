from django import forms
from .models import Listing, Category

class ListingForm(forms.Form):
    name = forms.CharField(
        label = "Name",
        widget = forms.TextInput()
    )
    description = forms.CharField(
        label = "Description",
        widget = forms.Textarea()
    )
    price = forms.DecimalField(
        label = "Price",
        min_value = 0,
        decimal_places = 2,
        max_digits = 10,
        widget = forms.NumberInput()
    )
    # might have to add an url instead of an actual image that will then be saved
    photo = forms.URLField(
        required = False
    )

    category = forms.ModelChoiceField(
        queryset = Category.objects.all(),
        empty_label = "Choose a category",
        widget = forms.Select()
    )

    class Meta:
        model  = Listing                 
        fields = ["name", "description", "price", "photo",
                  "category", "active"]   
        
class BidForm(forms.Form):
    bid = forms.DecimalField(
        label = "",
        min_value = 0,
        decimal_places = 2,
        max_digits = 10,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter your bid'
        })
    )

class CommentForm(forms.Form):
    comment = forms.CharField(
        label = "",
        widget=forms.Textarea(attrs={
            'class': 'commentForm'
        })
    )