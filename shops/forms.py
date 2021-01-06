from django import forms
from .models import Item

PAYMENT_CHOICES = (
	('S', 'Stripe'),
	('M', 'Mpesa')
)

class CheckoutForm(forms.Form):
	town = forms.CharField(widget=forms.TextInput(attrs={
		'class': 'form-control'
		}))
	phone = forms.CharField(required=False, widget=forms.NumberInput(attrs={
		'class': 'form-control'
		}))
	id_number = forms.CharField(required=False, widget=forms.NumberInput(attrs={
		'class': 'form-control'
		}))
	same_shipping_address = forms.BooleanField(required=False)
	save_info = forms.BooleanField(required=False)
	payment_option = forms.ChoiceField(
		widget=forms.RadioSelect, choices=PAYMENT_CHOICES)



class StockSearchForm(forms.ModelForm):
	title = forms.CharField(widget=forms.TextInput(attrs={
		'class': 'form-control'
		}))
	# export_to_CSV = forms.BooleanField(required=False)
	class Meta:
		model = Item
		fields = ['title']


class CouponForm(forms.Form):
	code = forms.CharField(widget=forms.TextInput(attrs={
		'class':'form-control',
		'placeholder': 'Promo code',
		'aria-label': 'Recipient\'s username',
		'aria-describedy': 'basic-addon2'
		}))