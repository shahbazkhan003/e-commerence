from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    locality = models.CharField(max_length=200)  
    city = models.CharField(max_length=200)
    zip_code = models.IntegerField()
    state = models.CharField(max_length=200)

    def __str__(self):
        return str(self.id)

CATAGERY_CHOICE = (
    ('M', 'Mobile'),
    ('L', 'Laptop'),
    ('TW', 'Top Wear'),
    ('BW', 'Bottom Wear')
)

class Product(models.Model):
    title = models.CharField(max_length=100)
    selling_price = models.FloatField()
    discount_price = models.FloatField()
    description = models.TextField()
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=2, choices=CATAGERY_CHOICE)  
    product_image = models.ImageField(upload_to='productimg')
    created_date = models.DateTimeField(auto_now_add=True)

def __str__(self):
    return str(self.id)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    

def __str__(self):
    return str(self.user)

STATE_CHOICE = (
    ('Accepted', 'Accepted'),
    ('Paked' , 'Packed'),
    ('On The Way' , 'On The Way'),
    ('Delivered','Delivered'),
    ('Cancel','Cancel')
)    

class OrderPlaced(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATE_CHOICE, default='Pending')
    
    def __str__(self):
        return str(self.id)

