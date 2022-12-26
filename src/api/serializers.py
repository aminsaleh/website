from rest_framework import serializers
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import *


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'phone',
            'address',
            'birthday',
            'password',
        )
        model = get_user_model()
    
    def validate_username(self, username):
        return username.lower()
    
    def validate_email(self, email):
        return email.lower()
    
    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.address = validated_data.get('address', instance.address)
        instance.birthday = validated_data.get('birthday', instance.birthday)
        instance.set_password(validated_data['password'])
        instance.save()

        return instance



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
