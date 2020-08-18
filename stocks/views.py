from django.shortcuts import render

# Create your views here.
from .models import Stock

def home(request):
	title = "Welcome : this to the store"

	context = {
	"title" : title
	}
	return render(request, "home.html", context)

def list_items(request):
	querySet = Stock.objects.all()

	context = {
		"querySet": querySet
	}

	return render(request, "list_items.html", context)