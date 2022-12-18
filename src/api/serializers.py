from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *


class UserSerializer(serializers.ModelSerializer):

    def validate_username(self, username):
        return username.lower()
    
    class Meta:
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'phone',
            'address',
            'birthday',
        )
        model = get_user_model()
        # model = models.User


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Product


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = '__all__'
