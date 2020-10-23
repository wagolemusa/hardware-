from django.db import models
from django.views.generic import ListView, DetailView
# Create your models here.
from django.conf import settings
from django.shortcuts import reverse

class Item(models.Model):
	title = models.CharField(max_length=100)
	price = models.FloatField()
	discout_price = models.FloatField(blank=True, null=True)
	slug = models.SlugField()
	quantity = models.IntegerField(default=1)

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("shops:product", kwargs={
			'slug': self.slug
		})

	def get_add_to_cart_url(self):
		return reverse("shops:add_to_cart", kwargs={
			'slug': self.slug
		})

	def get_remove_from_cart_url(self):
		return reverse("shops:remove_from_cart", kwargs={
			'slug': self.slug
		})

class OrderItem(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, 
		on_delete=models.CASCADE)
	ordered = models.BooleanField(default=False)
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)

	def __str__(self):
		return "%s  %s" %(self.quantity, self.item.title)

class Order(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	items = models.ManyToManyField(OrderItem)
	start_date = models.DateTimeField(auto_now_add=True)
	ordered_date = models.DateTimeField()
	ordered = models.BooleanField(default=False)

	def __str__(self):
		return self.user.username

