from django.shortcuts import render, redirect
# Create your views here.
from .models import Stock
from .forms import *
from django.http import HttpResponse
import csv
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def home(request):
	title = "Welcome : this to the store"
	context = {
	"title" : title
	}
	return render(request, "home.html", context)

@login_required
def list_items(request):
	form = StockSearchForm(request.POST or None)
	querySet = Stock.objects.all()
	context = {
		"querySet": querySet,
		"form":form
	}
	if request.method == 'POST':
		querySet = Stock.objects.filter(item_name__icontains=form['item_name'].value())

	if form['export_to_CSV'].value() == True:
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachement; filename="List of stock.csv"'
		writer = csv.writer(response)
		writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY'])
		instance = querySet
		for stock in instance:
			writer.writerow([stock.category, stock.item_name, stock.quantity])
		return response

	context = {
		"form":form,
		"querySet": querySet
	}	 
	return render(request, "list_items.html", context)

@login_required
def add_items(request):
	form = StockCreateForm(request.POST or None)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, 'Successfully Saved')
		return redirect('/list_items')
	context = {
		"form":form,
		"title" :"Add Item"
	}
	return render(request, "add_items.html", context)

@login_required
def update_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form =  StockUpdateForm(instance=queryset)
	if request.method == 'POST':
		form = StockUpdateForm(request.POST, instance=queryset)
		if form.is_valid():
			form.save()
			messages.success(request, 'Successfully Updated')
			return redirect('/list_items')

	context = {
		'form':form
	}
	return render(request, 'add_items.html', context)

@login_required
def delete_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	if request.method == 'POST':
		queryset.delete()
		messages.success(request, 'Successfully Deleted')
		return redirect('/list_items')
	return render(request, 'delete_items.html')

def stock_details(request, pk):
	queryset = Stock.objects.get(id=pk)
	context = {
		"queryset": queryset
	}
	return render(request, 'stock_details.html', context)

@login_required
def issue_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form  = IssueForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.quantity -= instance.issue_quantity
		# instance.issue_by = str(request.user)
		messages.success(request, "Issued successfully." + " " + str(instance.quantity) + " " + str(instance.item_name) + "s now left in store")
		instance.save()
		return redirect('/stock_details/' + str(instance.id))
	context = {
		"title": 'Issue ' + str(queryset.item_name),
		"queryset": queryset,
		"form": form,
		# "username": 'Issue By: ' str(request.user),
	}
	return render(request, "add_items.html", context)

@login_required
def receive_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form  = ReceiveForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.quantity += instance.issue_quantity
		# instance.issue_by = str(request.user)
		messages.success(request, "Issued successfully." + " " + str(instance.quantity) + " " + str(instance.item_name) + "s now left in store")
		instance.save()
		return redirect('/stock_details/' + str(instance.id))
	context = {
		"title": 'Issue ' + str(queryset.item_name),
		"queryset": queryset,
		"form": form,
		# "username": 'Issue By: ' str(request.user),
	}
	return render(request, "add_items.html", context)

@login_required
def reoder_level(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = ReoderLevelForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, "Reorder level for " +str(instance.item_name) + "is updated to " + str(instance.reoder_level))
		return redirect('/list_items')
	context = {
		"instance":queryset,
		"form":form
	}
	return render(request, "add_items.html", context)