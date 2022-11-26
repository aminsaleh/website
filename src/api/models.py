from django.db import models
from django.core.validators import RegexValidator

class User(models.Model):
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=64)
    username = models.CharField(
        unique=True,
        max_length=50,
        validators=[RegexValidator(regex=r'^[A-Za-z_](\w){3,49}')]
    )
    password = models.CharField(max_length=64)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=11,
        validators=[RegexValidator(regex=r'[0-9]{11}')],
    )
    address = models.TextField()
    birthday = models.DateField(null=True, blank=True)
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    code = models.CharField(max_length=3)
    description = models.TextField()
    images = models.ImageField()
    in_stock = models.IntegerField()
    score_sum = models.FloatField()
    score_num = models.IntegerField()
    score = models.FloatField()
    
class Order(models.Model):
    
    status = models.CharField(
        choices=[
            ("bs", "basket"),
            ("og", "on_going"),
            ("dl", "delivered")
        ],
        max_length=20,
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

class Comment(models.Model):
    text = models.TextField()
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
    )
