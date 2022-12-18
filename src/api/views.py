from django.shortcuts import render
from loguru import logger
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializers import *



class CostumePermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        """
        Returns `True` if the user is authenticated.
        SAFE_METHODS are : 'GET' , 'HEAD' , 'OPTIONS'
        """

        authentication_reqs = ['GET','PUT','PATCH','DELETE']
        requset_method = request.method
        user_authenticated = request.user.is_authenticated

        if requset_method=='POST':
            return True

        if (requset_method in authentication_reqs) and (user_authenticated):
            return True
        
        return False



class UserView(APIView):

    permission_classes = [CostumePermissions]

    # getInfo
    def get(self, request):

        # request.session
        
        username = request.GET["username"]

        if username==request.user.username:
            account_info = User.objects.get(
                username=username
            )
            serializer = UserSerializer(account_info)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        else:
            return Response(
                {'message': 'User Not Found!'},
                status=status.HTTP_404_NOT_FOUND
            )

    # register
    def post(self, request):
        
        url_path = request.path_info

        if url_path=="/accounts/register":
            # create new account

            account_info = {
                "first_name": request.data['first_name'],
                "last_name": request.data['last_name'],
                "email": request.data['email'],
                "username": request.data['username'],
                "password": request.data['password'],
                "confirm_password": request.data['confirm_password'],
            }

            # check username and password
            account_info['username'] = account_info['username'].lower()
            account_info['email'] = account_info['email'].lower()

            if not account_info['password'] or not account_info['confirm_password']:
                return Response(
                    {"status":"Empty Password"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if account_info['password']!=account_info['confirm_password']:
                return Response(
                    {"status":"Mismatch"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # create unconfirmed user in db
            try:
                user = User.objects.create(
                    first_name=account_info['first_name'],
                    last_name=account_info['last_name'],
                    email=account_info['email'],
                    username=account_info['username'],
                    password=account_info['password'],
                    is_confirmed=False,
                    confirmation_token='', # create a token for the user
                )
            except Exception as e:
                return Response(
                    {"status": "username or email is not unique!"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                user.set_password(account_info['password'])
                user.save()
                return Response(
                    {"status": "user registered successfully"},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                pass


        elif url_path=="/accounts/confirm":
            # redirect from email confirmation
            # check the user request and user token in db
            # if they are the same make the user confirmed
            # if not send another token email to the user 
            return Response(
                {"status":"email confirmed"},
                status=status.HTTP_200_OK
            )

        else:
            # useless code!
            return Response(
                {"status":"url not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    # update
    def put(self, request):

        # request.session

        account_info = {
            "first_name": request.data['first_name'],
            "last_name": request.data['last_name'],
            # "email": request.data['email'],
            "username": request.data['username'],
            # "password": request.data['password'],
        }
        
        try:
            user = User.objects.filter(username=account_info['username'])        
        except Exception as e:
            return Response(
                {"status":"user not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # email confirmation
        
        try:
            user.update(
                first_name='ddd',
                last_name='sss',
                username=account_info['username'],
                # password=user.set_password(account_info['password'])
            )
            
            return Response(
                {"status":"user updated successfully"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # forget
    def patch(self, request):

        # request.session

        pass

    # delete account
    def delete(self, request):
        pass



class ProductView(APIView):

    # permission_classes = [permissions.IsAuthenticated]
    
    # getAll
    def get(self, request):
        products = Product.objects.all()

        # get categories and check for checked categories
        # get price range and select the products in the range
        # select the product id if there is an id
        # check for sorted check box
        # check the product name if there is a name

        serializer = ProductSerializer(products, many=True)
        if products:
            return Response(serializer.data)
        else:
            return Response({'products': 'no'}, status=status.HTTP_404_NOT_FOUND)


    # ProductGetById
    def post(self, request):
        pass


class OrderView(APIView):
    pass

