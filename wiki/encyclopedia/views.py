from django.shortcuts import render
from django.http import HttpResponse
from . import util
from markdown2 import Markdown
from django import forms
from django.shortcuts import redirect
from random import randint

# Form for Create New Page
# This form will store the values of the controls as vars
class newCreatePageForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea, label="Content")

def index(request):
    # Handle when there are some GET parameters
    query = request.GET.get('q') 
    random = request.GET.get('rand')

    if query:
        entry = util.get_entry(query)

        if entry:
           return HttpResponse(wiki(request, query)) 
        else:
            return HttpResponse(searchResults(request, query)) 

    if random == "true":
        return HttpResponse(wiki(request, randomPage())) 

    # Default page
    else:
        return render(request, "encyclopedia/index.html", {
            # These are the variables that we are giving to the html
            "entries": util.list_entries()
        })

def wiki(request, title):
    entry = util.get_entry(title)
    markdown = Markdown()
    if entry is None:
        return render(request, "encyclopedia/error.html")
    else:
        return render(request, "encyclopedia/wiki.html", {
            "title": title,
            "entry": markdown.convert(entry)
        })

def searchResults(request, query):
    listQuery = []
    listEntries = util.list_entries()
    
    # For each entry check if query is a substring
    for entry in listEntries:
        if query in entry:
            listQuery.append(entry)

    return render(request, "encyclopedia/searchResults.html", {
        "listEntries": listQuery
    })

def createNewPage(request):
    # Handle when request is POST to add the new page to the DB
    if request.method == "POST":
        form = newCreatePageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"] 
            util.save_entry(title, content)
            return redirect("wiki", title=title)

    # Default view
    return render(request, "encyclopedia/createNewPage.html", {
        "form": newCreatePageForm()
    })

def randomPage():
    listEntries = util.list_entries()
    randomIndex = randint(0, len(listEntries) - 1)
    return listEntries[randomIndex]