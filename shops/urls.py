from django.urls import path

from .views import (
	index,
	item_list,
	products,
	add_to_cart,
	remove_from_cart
)


app_name = 'shops'

urlpatterns = [
	path('', index, name = 'index'),
	path('shops/item_list', item_list, name='item_list'), 
	path('product/<slug>/', products, name='product'),
	path('add_to_cart/<slug>/', add_to_cart, name='add_to_cart'),
	path('remove_from_cart/<slug>/', remove_from_cart, name='remove_from_cart')
]