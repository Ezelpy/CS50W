from django.shortcuts import render
from django.http import HttpResponse
from . import util
from markdown2 import Markdown
from django import forms
from django.shortcuts import redirect

class newCreatePageForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea, label="Content")

def index(request):
    if request.GET.keys():
        query = request.GET.get('q') 
        entry = util.get_entry(query)
        if entry:
           return HttpResponse(wiki(request, query)) 
        else:
            return HttpResponse(searchResults(request, query)) 

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

    for entry in listEntries:
        if query in entry:
            listQuery.append(entry)

    return render(request, "encyclopedia/searchResults.html", {
        "listEntries": listQuery
    })

def createNewPage(request):
    if request.method == "POST":
        form = newCreatePageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return redirect("wiki", title=title)

    return render(request, "encyclopedia/createNewPage.html", {
        "form": newCreatePageForm()
    })