from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from .models import Item, OrderItem, Order, BillingAddress, Payment, Coupon, Category, Cash, Mpesapay 
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .forms import *
import stripe
import random
import string	
import requests
import africastalking
import ssl
import json
import datetime
import base64
from requests.auth import HTTPBasicAuth
# from datetime import datetime, timedelta
stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"

def create_ref_code():
	return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def index(request):
	items = Item.objects.all()

	cat = Category.objects.all()
	context = {
		'items': items,
		'cat':cat,
	}
	return render(request, "index.html", context)

def item_list(request):
	context = {
		# 'item':Item.objects.all()
	}
	return render(request, "item_list.html", context)

def products(request, id=None):
	instance = get_object_or_404(Item, id=id)
	# instance = Item.filter(slug=slug)
	# category = get_object_or_404(Category, id=id)
	# category = Category.objects.get(id=id)
	show = Item.objects.all()
	cat = Category.objects.all()
	context = {
		"instance":instance,
		"show":show,
		"cat":cat
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


def category(request, id=None):
	categories = Category.objects.all()
	if id:
		category = get_object_or_404(Category, id=id)
		item = Item.objects.filter(category=category)
		cat = Category.objects.all()
		
	context = {
		'categories': categories,
		'category': category,
		'item':item,
		"cat":cat
	}
	return render(request, "category.html", context)

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
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			form = CheckoutForm()
			context = {
				'form': form,
				'CouponForm': CouponForm(),
				'order': order,
				'DISPLAY_COUPON_FORM':True
			}
			return render(self.request, "checkout.html", context)
		except ObjectDoesNotExist:
			messages.info(self.request, "You do not have an active order")
			return redirect("shops:checkout")


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
					id_number=id_number,
					# address_type = 'B'
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
		if order.billing_address:

			context = {
				'order':order,
				'DISPLAY_COUPON_FORM':False
			}
		else:
			messages.error(
				self.request, "You have not added a billung address")
			return redirect("shops:checkout")


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

			order_items = order.items.all()
			order_items.update(ordered=True)
			for item in order_items:
				item.save()
				
			order.ordered = True
			order.payment = payment
			# assign ref code
			order.ref_code.create_ref_code()
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
def add_to_cart(request, id=None):
	item = get_object_or_404(Item, id=id)
	order_item, created  = OrderItem.objects.get_or_create(
			item=item,
			user=request.user,
			ordered=False
		)
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		# check if the order item is in the order
		if order.items.filter(item__id=item.id).exists():
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
def remove_from_cart(request, id=None):
	item = get_object_or_404(Item, id=id)
	# Check if user has orders
	order_qs = Order.objects.filter(
		user=request.user,
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]

		if order.items.filter(item__id=item.id).exists():
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
			return redirect("shops:product", id=id)			
	else:
		messages.info(request, "You do not have an active order")
		return redirect("shops:product", id=id)


""" Remove Form Cart """
@login_required
def remove_single_from_cart(request, id=id):
	item = get_object_or_404(Item, id=id)
	# Check if user has orders
	order_qs = Order.objects.filter(
		user=request.user,
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]

		if order.items.filter(item__id=item.id).exists():
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
			return redirect("shops:product", id=id)			
	else:
		messages.info(request, "You do not have an active order")
		return redirect("shops:product", id=id)


def get_coupon(request, code):
	try:
		coupon = Coupon.objects.get(code=code)
		return coupon
	except ObjectDoesNotExist:
		messages.info(request, "This coupon does not exist")
		return redirect("shops:checkout")

class AddCouponView(View):
	def post(self, *args, **kwargs):
		form = CouponForm(self.request.POST or None)
		if form.is_valid():
			try:
				code = form.cleaned_data.get('code')
				order = Order.objects.get(
        	user=self.request.user, ordered=False)
				order.coupon = get_coupon(self.request, code)
				order.save()
				messages.success(self.request, "Successfully added coupon")
				return redirect("shops:checkout")
			except ObjectDoesNotExist:
				messages.info(self.request, "You do not have an active order")
		return redirect("shops:checkout")

class RequestRefundView(View):
	def get(self, *args, **kwargs):
		form = RefundForm()
		context = {
			'form': form
		}
		return render(self.request, "request_refund.html", context)

	def post(self, *args, **kwargs):
		form = RefundForm(self.request.POST or None)
		if form.is_valid():
			ref_code = form.cleaned_data.get('ref_code')
			message = form.cleaned_data.get('message')
			email = form.cleaned_data.get('email')
			# edit the order
			try:
				order = Order.objects.get(ref_code=ref_code)
				order.refund_requested = True
				order.save()

				# store the refund
				refund = Refund()
				refund.order = order
				refund.reason = message
				refund.email = email
				refund.save()

				messages.info(self.request, "You request was received")
				return redirect("shops:request-refund")
			except ObjectDoesNotExist:
				messages.info(self.request, "This order does not exit.")
				return redirect("shops:request-refund")

class RequestRefundView(View):
	def get(self, *args, **kwargs):
		form = RefundForm()
		context = {
			'form':form
		}
		return render(self.request, "request_refund.html", context)

	def post(self, *args, **kwargs):
		form = RefundForm(self.request.POST)
		if form.is_valid():
			ref_code = form.cleaned_data.get('ref_code')
			message = form.cleaned_data.get('message')
			email = form.cleaned_data.get('email')
			# edit the order
			# This checks if the ref-code exits
			try:
				order = Order.objects.get(ref_code=ref_code)
				order.refund_requested = True
				order.save()

				# store the return
				refund = Refund()
				refund.order = order
				refund.reason = message
				refund.email = email
				refund.save()

				messages.info(self.request, "Your request was recived")
				return redirect("shops:request-refund")

			except ObjectDoesNotExist:
				messages.info(self.request, "This order does not exist")
				return redirect("shops:request-refund")

# Cash payment on Desktop
@method_decorator(login_required, name='dispatch')
class CashDesk(LoginRequiredMixin, View):
	def get(self, *args, **kwargs):
		form = CashPay()
		order = Order.objects.get(user=self.request.user, ordered=False)
		context = {
		
			'order': order,
			'form': form
		}
		return render( self.request, "cashmaney.html", context)
	
	def post(self, *args, **kwargs):
	
		order = Order.objects.get(user=self.request.user, ordered=False)
		amount = int(order.get_total())
		cashpay = Cash()
		cashpay.user = self.request.user
		cashpay.amount = amount
		cashpay.save()
		# except ObjectDoesNotExist:
		
		# order_items = order.items.all()
		# order_items.update(ordered=True)
		# for item in order_items:
		# 	item.save()
		order_items = Order.objects.filter(user = self.request.user, ordered=False)
		order_items.update(ordered=True)
		for item in order_items:
			item.save()

		reciept = 'payed'
		orderpay = Order.objects.filter(user = self.request.user, pay='notpayed')
		orderpay.update(pay=reciept)


		messages.info(self.request, "You do not have an active oredr")
		return redirect("shops:printcash")

@method_decorator(login_required, name='dispatch')
class CashDeskprint(LoginRequiredMixin, View):
	def get(self, *args, **kwargs):
		order = Order.objects.filter(user=self.request.user, pay='payed').order_by('-timestamp')[:1]
		# cash = "SELECT * FROM shops_order WHERE ordered = 'True'"
		# order = Order.objects.raw(cash)
		# order = Cash.objects.filter(user=self.request.user).order_by('-timestamp')
		# tatol = Order.objects.aggregate(sum())
		context = {
			'order': order
		}
		return render( self.request, "printcash.html", context)
	

# Mpesa implimataions
# @login_required
@method_decorator(login_required, name='dispatch')
class Mpesa(LoginRequiredMixin, View):
	def get(self, *args, **kwargs):
		form = Mpesaform()
		order = Order.objects.get(user=self.request.user, ordered=False)
		context = {
			'order': order,
			'form': form
		}
		return render(self.request, "mpesa.html", context)

	def post(self, *args, **kwargs):
		form = Mpesaform(self.request.POST or None)
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			amount = int(order.get_total())
			print(amount)
			if form.is_valid():
				phone = form.cleaned_data.get('phone')

				pay_bills = Mpesapay()
				pay_bills.user = self.request.user
				pay_bills.phone=phone
				pay_bills.amount=amount
				pay_bills.save()
				
				# Lipa na mpesa Functionality 
				consumer_key = "EKyBEUXldtz0pAlmfv6fDELROh5vwQH0"
				consumer_secret = "KADx7lxZWJdU0TcW"

				# api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" #AUTH URL
				api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

				r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

				data = r.json()
				access_token = "Bearer" + ' ' + data['access_token']

				#GETTING THE PASSWORD
				timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
				passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
				business_short_code = "174379"
				data = business_short_code + passkey + timestamp
				encoded = base64.b64encode(data.encode())
				password = encoded.decode('utf-8')
				# BODY OR PAYLOAD
				payload = {
				    "BusinessShortCode": business_short_code,
				    "Password": password,
				    "Timestamp": timestamp,
				    "TransactionType": "CustomerPayBillOnline",
				    "Amount": amount,
				    "PartyA": phone,
				    "PartyB": business_short_code,
				    "PhoneNumber": phone,
				    "CallBackURL": "https://hardwarekisumu.herokuapp.com/callbackurl",
				    "AccountReference": "account",
				    "TransactionDesc": "account"
				}

				#POPULAING THE HTTP HEADER
				headers = {
				    "Authorization": access_token,
				    "Content-Type": "application/json"
				}
				url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest" #C2B URL
				response = requests.post(url, json=payload, headers=headers)
				print (response.text)
				# return {"message": 'Wait Response on Your phone'}
				messages.success(self.request, "Wait Response on Your phone")
				return redirect("/")
		except ObjectDoesNotExist:
			messages.error(self.request, "You do not have an active order")
			return redirect("shops:order-summary")

# @login_required
@csrf_exempt
def callbackurl(request):
	# def get(self, *args, **kwargs):
	# 	# def callbackurl(self, request, *args, **kwargs):
	# current_user = request.user
	# 	print(current_user.username)
	# return HttpResponse("Welcome to poll's index!")
	"""
	It recieves the response from safaricam
	"""
	json_da = json.loads(request.body)
	print(json_da)

	resultcode = json_da['Body']['stkCallback']['ResultCode']
	resultdesc = json_da['Body']['stkCallback']['ResultDesc']
	# phone = json_da["stkCallback"]["CallbackMetadata"]["Item"][4]["Value"]
	mpesa_reciept = "MPESA"
			
	# print(mpesa_reciept)
	def pay():
		if resultcode == 0:
			return "Paid"
		elif resultcode == 1:
			return "Faild"
		else:
			return "canceled"
	status = pay()
	print(status)

	callback = Mpesapay.objects.filter(cash='notpayed')
	callback.update(cash=status)
		
	if status == 'Paid':

		# @login_required
		# def get(self, *args, **kwargs):
		# order = Order.objects.filter(user = request.user, ordered='False')
		# print(order)
		order = Order.objects.filter(ordered=False)
		order.update(ordered=True)
		for item in order:
			item.save()

			# order.ordered = True
			# # order.payment = payment
			# order.save()
		phonecal = Mpesapay.objects.filter(phone__startswith='254').order_by('-timestamp')[:1].values()
		for call in phonecal:
			num = call['phone']
			phone = str(num)
			print(phone)
			# Sends sms to mobile phone
			message = "Thanks for shopping with Us, We'll deliver your product as soon as possible"
			username = "refuge"    # use 'sandbox' for development in the test environment
			api_key = "0baff8f7f0e3e0ca915aabe81477a7d444bd52c98afd11ff9b39079337db3901"      # use your sandbox app API key for development in the test environment
			africastalking.initialize(username, api_key)
			# Initialize a service e.g. SMS
			sms = africastalking.SMS
			# Use the service synchronously
			response = sms.send(message, ['+' + phone ])
		return HttpResponse("Welcome to poll's index!")

	else:
		phonecal =  phonecal = Mpesapay.objects.filter(phone__startswith='254').order_by('-timestamp')[:1].values()
		for call in phonecal:
			num = call['phone']
			phone = str(num)
			print(phone)
			# Sends sms to mobile phone
			message = "Your payments for shopping with Cosben hardware is %s. Please Try again https://cosben.co.ke"%(status)
			username = "refuge"    # use 'sandbox' for development in the test environment
			api_key = "0baff8f7f0e3e0ca915aabe81477a7d444bd52c98afd11ff9b39079337db3901"      # use your sandbox app API key for development in the test environment
			africastalking.initialize(username, api_key)
			# Initialize a service e.g. SMS
			sms = africastalking.SMS
			# Use the service synchronously
			response = sms.send(message, ['+' + phone ])
		return HttpResponse("Welcome to Cosben hardware")