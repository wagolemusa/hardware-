from django import forms
from .models import Item

class StockSearchForm(forms.ModelForm):
	title = forms.CharField(widget=forms.TextInput(attrs={
		'class': 'form-control'
		}))
	# export_to_CSV = forms.BooleanField(required=False)
	class Meta:
		model = Item
		fields = ['title']