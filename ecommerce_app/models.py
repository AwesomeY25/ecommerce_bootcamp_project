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
    confirmation_number = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Ensure price field is here