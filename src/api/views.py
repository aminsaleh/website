from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

from .serializers import *
from .models import *

class UserView(APIView):
    serializer_class = UserSerializer
    
    def get(self, request):
        req = request.data
        username = req['username']
        account_info = User.objects.filter(
            username=username,
        )
        serializer = UserSerializer(account_info)
        return Response(serializer.data)