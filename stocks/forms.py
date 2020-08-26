from django import forms
from .models import Stock

class StockCreateForm(forms.ModelForm):
	# category = forms.CharField(widget=forms.TextInput(attrs={
	# 	'class': 'form-control'
	# 	}))
	item_name = forms.CharField(widget=forms.TextInput(attrs={
		'class': 'form-control'
		}))
	quantity = forms.CharField(widget=forms.NumberInput(attrs={
		'class': 'form-control'
		}))

	class Meta:
		model = Stock
		fields = ['category', 'item_name', 'quantity']

	# def clean_category(self):
	# 		category = self.cleaned_data.get('category')
	# 		if not category:
	# 			raise forms.ValidationError('This field is required')
			
	# 		for instance in Stock.objects.all():
	# 			if instance.category == category:
	# 				raise forms.ValidationError(category + ' is aleady created')
	# 		return category

	def clean_item_name(self):
		item_name =  self.cleaned_data.get('item_name')
		if not item_name:
			raise forms.ValidationError('This field is required')
		return item_name

class StockSearchForm(forms.ModelForm):
	item_name = forms.CharField(widget=forms.TextInput(attrs={
		'class': 'form-control'
		}))
	export_to_CSV = forms.BooleanField(required=False)
	class Meta:
		model = Stock
		fields = ['item_name']

class StockUpdateForm(forms.ModelForm):
	class Meta:
		model = Stock
		fields = ['category', 'item_name', 'quantity']

class IssueForm(forms.ModelForm):
	class Meta:
		model = Stock
		fields = ['issue_quantity', 'issue_to']

class ReceiveForm(forms.ModelForm):
	class Meta:
		model = Stock
		fields = ['receive_quantity']

class ReoderLevelForm(forms.ModelForm):
	class Meta:
		model = Stock
		fields = ['reoder_level']