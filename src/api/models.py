from django.db import models


class User(models.Model):
    first_name = models.CharField()
    last_name = models.CharField()
    username = models.CharField(unique=True)
    password = models.CharField()
    email = models.CharField()
    phone = models.CharField()
    address = models.TextField()
    
class Product(models.Model):
    name = models.CharField()
    price = models.IntegerField()
    code = models.CharField()
    des = models.TextField()
    images = models.ImageField()
    in_stock = models.IntegerField()
    
class Order(models.Model):
    
    status = models.CharField(
        choices=["basket", "on_going", "delivered"]
    )
    purchase_time = models.DateTimeField(auto_now_add=True)
    deliver_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
    )
    selected_product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
    )
    product_count = models.IntegerField()
    order_id = models.CharField(max_length=64)

