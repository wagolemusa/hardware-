from django.contrib import admin

# Register your models here.
from .models import Item, OrderItem, Order, Payment, BillingAddress, Coupon, Refund, Category, Cash,Mpesapay

def make_refund_accepted(modeladmin, request, queryset):
	queryset.update(refund_requested=False, refund_granted=True)
make_refund_accepted.short_description = 'Update order to refund granted'

class OrderAdmin(admin.ModelAdmin):
	list_display = [
									'user', 
									'ordered',
									'being_delivered',
									'received_requested',
									'refund_requested',
									'refund_granted',
									'billing_address',
									'payment',
									'coupon',
									'timestamp']
	list_display_links = [
							'user',
							'billing_address',
							'payment',
							'coupon'
							]
	list_filter = [
									'user', 
									'ordered',
									'being_delivered',
									'received_requested',
									'refund_requested',
									'refund_granted']
									
	search_fields = [
		'user__username',
		'ref_code'
	]

	actions = [make_refund_accepted]

class CategoryAdmin(admin.ModelAdmin):
	list_display = [
			'name'
	]

class CashAdmin(admin.ModelAdmin):
	list_display = [
		'user',
		'amount',
		'timestamp'
	]


class OrderItemAdmin(admin.ModelAdmin):
	list_display = [
		'user',
		'item',
		'quantity',
		'ordered',
		'timestamp'

	]

class MpesapayAdmin(admin.ModelAdmin):
	list_display = [
		"user",
		"amount",
		"phone",
		"cash",
		"timestamp",
	]

admin.site.register(Item)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Payment)
admin.site.register(BillingAddress)
admin.site.register(Coupon)
admin.site.register(Cash, CashAdmin)
admin.site.register(Mpesapay, MpesapayAdmin)