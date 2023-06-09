from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Product(models.Model):
    _id = models.AutoField(primary_key=True, editable=False),
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=50, null=False, blank=False)
    brand = models.CharField(max_length=50, null=False, blank=False)
    category = models.CharField(max_length=50, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    rating = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    numOfReviews = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    countInStock = models.IntegerField(default=0)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return self.name

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    rating = models.IntegerField(default=0)
    comment = models.TextField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    _id = models.AutoField(primary_key=True, editable=False)

    class Meta:
        db_table = 'reviews'

    def __str__(self):
        return str(self.rating)
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    paymentMethod = models.CharField(max_length=200, null=True, blank=True)
    taxPrice = models.DecimalField(max_digits=7, decimal_places=2)
    shippingPrice = models.DecimalField(max_digits=7, decimal_places=2)
    productsPrice = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    totalPrice = models.DecimalField(max_digits=7, decimal_places=2)
    shippingAddress = models.TextField()
    isPaid = models.BooleanField(default=False)
    paidAt = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    isDelivered = models.BooleanField(default=False)
    deliveredAt = models.DateTimeField(
        auto_now_add=False, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    _id = models.AutoField(primary_key=True, editable=False)

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return str(self.createdAt)

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    qty = models.IntegerField(null=True, blank=True, default=0)
    _id = models.AutoField(primary_key=True, editable=False)

    class Meta:
        db_table = 'order_items'

    def __str__(self):
        return str(self.name)