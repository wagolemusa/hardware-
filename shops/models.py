from django.db import models
from django.views.generic import ListView, DetailView
# Create your models here.
from django.conf import settings
from django.shortcuts import reverse
from django.db.models.signals import pre_save
from django.utils.text import slugify

ADDRESS_CHOICES = (
	('B', 'Billing'),
	('S', 'Shipping')
)

class Category(models.Model):
	name = models.CharField(max_length=30)

	def __str__(self):
		return self.name

	def get_category_absolete_url(self):
		return reverse('shops:category', args=[self.id])

class Item(models.Model):
	category = models.ForeignKey(Category, on_delete=models.CASCADE,
                    related_name="category_set")
	title = models.CharField(max_length=100)
	price = models.FloatField()
	discout_price = models.FloatField(blank=True, null=True)
	quantity = models.IntegerField(default=1)
	image = models.ImageField()
	content = models.TextField()

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("shops:product", kwargs={
			"id": self.id
		})

	def get_add_to_cart_url(self):
		return reverse("shops:add_to_cart", kwargs={
			'id': self.id
		})

	def get_remove_from_cart_url(self):
		return reverse("shops:remove_from_cart", kwargs={
			'id': self.id
		})




class OrderItem(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, 
		on_delete=models.CASCADE)
	ordered = models.BooleanField(default=False)
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)

	def __str__(self):
		return "%s  %s" %(self.quantity, self.item.title)

	""" Get the Total """
	def get_total_price(self):
		return self.quantity * self.item.price

	""" Get the Discount """
	def get_total_discount_item_price(self):
		return self.quantity * self.item.discout_price

	""" Get amout saved """
	def get_amout_saved(self):
		return self.get_total_price() - self.get_total_discount_item_price()

	def get_final_price(self):
		if self.item.discout_price:
			return self.get_total_discount_item_price()
		return self.get_total_price()

class Order(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,
													on_delete=models.CASCADE)
	ref_code = models.CharField(max_length=20)
	items = models.ManyToManyField(OrderItem)
	start_date = models.DateTimeField(auto_now_add=True)
	ordered_date = models.DateTimeField()
	ordered = models.BooleanField(default=False)
	billing_address = models.ForeignKey(
		'BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)
	payment = models.ForeignKey(
		'Payment', on_delete=models.SET_NULL, blank=True, null=True)
	coupon = models.ForeignKey(
		'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
	being_delivered = models.BooleanField(default=False)
	received_requested = models.BooleanField(default=False)
	refund_requested = models.BooleanField(default=False)
	refund_granted = models.BooleanField(default=False)

	def __str__(self):
		return self.user.username

	def get_total(self):
		total = 0
		for order_item in self.items.all():
			total += order_item.get_final_price()
		if self.coupon:
			total -= self.coupon.amount
		return total

class BillingAddress(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,
														on_delete=models.CASCADE)
	town = models.CharField(max_length=100)
	phone = models.BigIntegerField(blank=True, null=True)
	id_number = models.BigIntegerField(blank=True, null=True)
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return self.user.username


class Payment(models.Model):
	stripe_change_id = models.CharField(max_length=50)
	user = models.ForeignKey(settings.AUTH_USER_MODEL,
														on_delete=models.CASCADE)
	amount = models.FloatField()
	timestamp = models.DateTimeField(auto_now_add=True)

	def __init__(self):
		return self.user.username

class Coupon(models.Model):
	code = models.CharField(max_length=15)
	amount = models.FloatField()

	def __str__(self):
		return self.code

class Refund(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	reason = models.TextField()
	accepted = models.BooleanField(default=False)
	email = models.EmailField(max_length=100)

	def __str__(self):
		return "%s" %(self.pk)


