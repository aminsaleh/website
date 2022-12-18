from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import User, Product

admin.site.register(get_user_model())
admin.site.register(Product)
