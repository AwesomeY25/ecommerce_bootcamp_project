from django import forms
from .models import Product

class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=100)
    address = forms.CharField(max_length=255)
    payment_info = forms.CharField(max_length=100)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'stock', 'image', 'tags']

    tags = forms.CharField(widget=forms.Textarea, help_text='Enter tags separated by commas')

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if not tags:
            raise forms.ValidationError("This field is required.")
        # Split the tags by commas and strip any whitespace
        tags_list = [tag.strip() for tag in tags.split(',')]
        return ','.join(tags_list)
