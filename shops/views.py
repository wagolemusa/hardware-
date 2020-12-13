from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from .models import Item, OrderItem, Order, BillingAddress, Payment
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin 
from .forms import *
import stripe
stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"

def index(request):
	context = {
		'items': Item.objects.all()
	}
	return render(request, "index.html", context)

def item_list(request):
	context = {
		# 'item':Item.objects.all()
	}
	return render(request, "item_list.html", context)

def products(request, slug):
	instance = get_object_or_404(Item, slug=slug)
	# instance = Item.filter(slug=slug)

	context = {
		"instance":instance,
	}
	return render(request, "product.html", context)

""" Customer List """
def costomer_list(request):
	form = StockSearchForm(request.POST or None)
	querySet = Item.objects.all()
	# context = {
	# 	"querySet": querySet,
	# 	"form":form
	# }
	if request.method == 'POST':
		querySet = Item.objects.filter(title__icontains=form['title'].value())
		
	# querySet = Item.objects.all()
	context = {
		'querySet': querySet,
		"form":form
	}
	return render(request, "costomer_list.html", context)


# class ItemDetailveiw(DetailView):
# 	model = Item
# 	template_name = "product.html"

class OrderSummaryView(LoginRequiredMixin, View):
	def get(self, *args, **kwargs):
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			context = {
				'object': order
			}
			return render(self.request, 'order-summary.html', context)
		except ObjectDoesNotExist:
			messages.error(self.request, "You do not have an active order")
			return redirect("/")

class CheckoutView(View):
	def get(self, *args, **kwargs):
		# form
		form = CheckoutForm()
		context = {
			'form': form
		}
		return render(self.request, "checkout.html", context)


	def post(self, *args, **kwargs):
		form = CheckoutForm(self.request.POST or None)
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			if form.is_valid():
				town = form.cleaned_data.get('town')
				phone = form.cleaned_data.get('phone')
				id_number = form.cleaned_data.get('id_number')
				# same_shipping_address = form.cleaned_data.get('same_shipping_address')
				# save_info = form.cleaned_data.get('save_info')
				payment_option = form.cleaned_data.get('payment_option')
				
				billing_address = BillingAddress(
					user=self.request.user,
					town=town,
					phone=phone,
					id_number=id_number
				)
				billing_address.save()
				order.billing_address = billing_address
				order.save()
				# TODO: add redirect to the selected payment option

				if payment_option == 'S':
					return redirect('shops:payment', payment_option='stripe')
				elif payment_option == 'M':
					return redirect('shops:mpesa', payment_option='mpesa')
				else:
					messages.warning(self.request, "Failed checked")
					return redirect('core:checkout')
		except ObjectDoesNotExist:
			messages.error(self.request, "You do have an active order")
			return redirect("core:order-summary")
			
class PaymentView(View):
	def get(self, *args, **kwargs):
		order = Order.objects.get(user=self.request.user, ordered=False)
		context = {
			'order':order
		}
		return render(self.request, "payments.html", context)


	def post(self, *args, **kwargs):
		order = Order.objects.get(user=self.request.user, ordered=False)
		token = self.request.POST.get('stripeToken')
		# amount = int(order.get_total() * 100)
		try:
			charge = stripe.Charge.create(
	  		amount=20,
	  		currency="usd",
	  		source="token",
			)

			print(amount)
			# create payments
			payment = Payment()
			payment.stripe_charge_id = charge['id']
			payment.user = self.request.user
			payment.amount
			payment.save()

			order.ordered = True
			order.payment = payment
			order.save() 

			messages.success(self.request, "Your order was successfull")
			return redirect("/")

		except stripe.error.CardError as e:
			body = e.json_body
			err = body.get('error', {})
			# messages.error(self.request, f"{err.get('message')}")
			message.error(self.request, "%s" %(err.get('message')))
			return redirect("/")

		except stripe.error.RateLimitError as e:
		  # Too many requests made to the API too quickly
		  messages.error(self.request, "Rate limit error")
		  return redirect("/")

		except stripe.error.InvalidRequestError as e:
		  # Invalid parameters were supplied to Stripe's API
		  messages.error(self.request, "Invalid parameters")
		  return redirect("/")

		except stripe.error.AuthenticationError as e:
		  # Authentication with Stripe's API failed
		  # (maybe you changed API keys recently)
		  messages.error(self.request, "Not authenticated")
		  return redirect("/")

		except stripe.error.APIConnectionError as e:
		  # Network communication with Stripe failed
		  messages.error(self.request, "Network Error")
		  return redirect("/")
		except stripe.error.StripeError as e:
		  # Display a very generic error to the user, and maybe send
		  # yourself an email
		  messages.error(self.request, "Something went wrong. you were not charged. Please try again")
		  return redirect("/")
		except Exception as e:
		  # Something else happened, completely unrelated to Stripe
		  # Send an email to ourselves
		  messages.error(self.request, "A serious error occurred. We have been notified")
		  return redirect("/")

""" Add To Cart """
@login_required
def add_to_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_item, created  = OrderItem.objects.get_or_create(
			item=item,
			user=request.user,
			ordered=False
		)
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		# check if the order item is in the order
		if order.items.filter(item__slug=item.slug).exists():
			order_item.quantity += 1
			order_item.save()
			messages.info(request, "This item was updated.")
			return redirect("shops:order-summary")
		else:
			order.items.add(order_item)
			messages.info(request, "This item was added to your cart.")
			return redirect("shops:order-summary")
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(
			user=request.user, ordered_date = ordered_date)
		order.items.add(order_item)
		messages.info(request, "This item was added to your cart.")
		return redirect("shops:order-summary")


""" Remove Form Cart """
@login_required
def remove_from_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	# Check if user has orders
	order_qs = Order.objects.filter(
		user=request.user,
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]

		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False
			)[0]
			order.items.remove(order_item)
			messages.info(request, "This Item was removed from cart")
			return redirect("shops:order-summary")	
		else:
			messages.info(request, "This was not in Cart")
			return redirect("shops:product", slug=slug)			
	else:
		messages.info(request, "You do not have an active order")
		return redirect("shops:product", slug=slug)


""" Remove Form Cart """
@login_required
def remove_single_from_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	# Check if user has orders
	order_qs = Order.objects.filter(
		user=request.user,
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]

		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False
			)[0]
			if order_item.quantity > 1:
				order_item.quantity -= 1
				order_item.save()
			else:
				order.items.remove(order_item)
			messages.info(request, "This quantiy was updated")
			return redirect("shops:order-summary")	
		else:
			messages.info(request, "This was not in Cart")
			return redirect("shops:product", slug=slug)			
	else:
		messages.info(request, "You do not have an active order")
		return redirect("shops:product", slug=slug)
