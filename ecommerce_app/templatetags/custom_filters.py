from django import template
from ecommerce_app.models import Product  # Adjust the import based on your app structure

register = template.Library()

@register.filter
def get_item(products, product_id):
    try:
        return products.get(id=product_id)
    except Product.DoesNotExist:
        return None

@register.filter
def multiply(value, arg):
    try:
        return value * arg
    except (ValueError, TypeError):
        return value  # If something goes wrong, return the original value
