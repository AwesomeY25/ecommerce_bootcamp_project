from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/')
    tags = models.CharField(max_length=100, blank=True, help_text='Enter tags separated by commas')

    def __str__(self):
        return self.name
    
    def get_tags_list(self):
        return self.tags.split(',') if self.tags else []
    
    def set_tags_list(self, tags_list):
        self.tags = ','.join(tags_list)

class Order(models.Model):
    customer_name = models.CharField(max_length=255)
    confirmation_number = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    status = models.CharField(max_length=50, default='Pending')
    shipping_address = models.TextField()  # Added field for shipping address
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Added field for total price

    def __str__(self):
        return f"Order {self.confirmation_number} by {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Ensure price field is here

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Order {self.order.confirmation_number}"

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)  # e.g., 'Stripe', 'PayPal'
    status = models.CharField(max_length=50, default='Completed')  # Payment status

    def __str__(self):
        return f"Payment for Order {self.order.confirmation_number} - {self.status}"
    
class ContentPage(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    image = models.ImageField(upload_to='content_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    refund_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=50, default='Pending')  # e.g., 'Pending', 'Completed'

    def __str__(self):
        return f"Refund for Order {self.order.confirmation_number} - {self.status}"