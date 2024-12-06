from django import forms
from .models import ContentPage, Order, Refund
from .models import Product

class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=100)
    address = forms.CharField(max_length=255)
    payment_info = forms.CharField(max_length=100)
    
class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(choices=[('Pending', 'Pending'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')]),
        }

class ContentPageForm(forms.ModelForm):
    class Meta:
        model = ContentPage
        fields = ['title', 'slug', 'content', 'image']
        
class RefundForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = ['amount', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

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
