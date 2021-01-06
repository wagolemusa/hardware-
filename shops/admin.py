from django.contrib import admin

# Register your models here.
from .models import Item, OrderItem, Order, Payment, BillingAddress, Coupon

class OrderAdmin(admin.ModelAdmin):
	list_display = ['user', 'ordered']

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(BillingAddress)
admin.site.register(Coupon)