from django.shortcuts import render

from . import util
from markdown2 import Markdown

def index(request):
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



    

