from django import forms
from .models import ContentPage, Order, Refund

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