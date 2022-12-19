from django.shortcuts import render
from loguru import logger
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializers import *

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.core.mail import send_mail


class CostumePermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        authentication_reqs = ['GET','PUT','PATCH','DELETE']
        requset_method = request.method
        user_authenticated = request.user.is_authenticated

        if requset_method=='POST':
            return True
        if requset_method=='GET' and request.path_info=='/accounts/confirm':
            return True
        if (requset_method in authentication_reqs) and (user_authenticated):
            return True
            
        return False


class UserView(APIView):

    permission_classes = [CostumePermissions]

    # getInfo
    def get(self, request):

        # request.session
        
        url_path = request.path_info
        if url_path=='/accounts/getInfo':
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

        elif url_path=="/accounts/confirm":
            uidb64 = request.GET['uidb64']
            token = request.GET['token']

            if uidb64 is not None and token is not None:
                uid = urlsafe_base64_decode(uidb64)
                try:
                    user = User.objects.get(pk=uid)
                    if default_token_generator.check_token(user, token) and user.is_confirmed == False:
                        user.is_confirmed = True
                        user.save()
                        return Response(
                            {"status":"user confirmed"},
                            status=status.HTTP_200_OK
                        )
                except:
                    # if not send another token email to the user
                    return Response(
                        {"status":"email not confirmed"},
                        status=status.HTTP_400_BAD_REQUEST
                    )                    

        else:
            # useless code!
            return Response(
                {"status":"url not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    # register
    def post(self, request):
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

        try:
            user = User.objects.create(
                first_name=account_info['first_name'],
                last_name=account_info['last_name'],
                email=account_info['email'],
                username=account_info['username'],
                password=account_info['password'],
                is_confirmed=False,
            )
            user.set_password(account_info['password'])
            user.save()
        except Exception as e:
            return Response(
                {"status": "username or email is not unique!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # send confirmation email
        try:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            html_content = """<h3>Hello %s</h3>
            <a href='http://localhost:8000/confirm?uidb64=%s&token=%s'>
            click to confirm</a>""" % (account_info['username'], uid, token)

            subject = 'Confirmation Email'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            send_mail(subject, html_content, email_from, recipient_list)
            
            return Response(
                {"status": "user registered successfully"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"status":"there was a problem in sending email to the user"},
                status=status.HTTP_400_BAD_REQUEST
            )

    # update
    def put(self, request):

        # request.session

        account_info = {
            "first_name": request.data['first_name'],
            "last_name": request.data['last_name'],
            "email": request.data['email'],
            "username": request.data['username'],
            "phone": request.data['phone'],
            "address": request.data['address'],
            "birthday": request.data['birthday'],
        }
        
        try:
            user = User.objects.filter(username=account_info['username'])        
        except Exception as e:
            return Response(
                {"status":"user not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            user.update(
                first_name=account_info['first_name'],
                last_name=account_info['last_name'],
                email=account_info['email'],
                username=account_info['username'],
                phone=account_info['phone'],
                address=account_info['address'],
                birthday=account_info['birthday'],
                is_confirmed=False,              
            )
            
        except Exception as e:
            return Response(
                {"status":"updating user unsuccessfull"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # send confirmation email
        try:
            
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            html_content = """<h3>Hello %s</h3>
            <a href='http://localhost:8000/confirm?uidb64=%s&token=%s'>
            click to confirm</a>""" % (account_info['username'], uid, token)

            subject = 'Confirmation Email'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            send_mail(subject, html_content, email_from, recipient_list)
            
            return Response(
                {"status":"user updated successfully"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status":"there was a problem in sending email to the user"},
                status=status.HTTP_400_BAD_REQUEST
            )


    # forget
    def patch(self, request):

        # request.session

        account_info = {
            "email": request.data['email'],
            "username": request.data['username'],
            "phone": request.data['phone'],
            "old_password": request['old_password'],
            "new_password": request['new_password'],
            "confirm_new_password": request['confirm_new_password'],
        }
        
        # check username and password
        account_info['username'] = account_info['username'].lower()
        account_info['email'] = account_info['email'].lower()

        try:
            user = User.objects.filter(username=account_info['username'])        
        except Exception as e:
            return Response(
                {"status":"user not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not account_info['old_password'] and \
            not account_info['new_password'] or \
            not account_info['confirm_new_password']:
            return Response(
                {"status":"Empty Password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if account_info['password']!=account_info['confirm_password']:
            return Response(
                {"status":"Mismatch"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user.is_confirmed=False
            user.set_password(account_info['new_password'])
            user.save()
            
        except Exception as e:
            return Response(
                {"status":"updating user unsuccessfull"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # send confirmation email
        try:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            html_content = """<h3>Hello %s</h3>
            <a href='http://localhost:8000/confirm?uidb64=%s&token=%s'>
            click to confirm</a>""" % (account_info['username'], uid, token)

            subject = 'Confirmation Email'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            send_mail(subject, html_content, email_from, recipient_list)
            
            return Response(
                {"status":"user updated successfully"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status":"there was a problem in sending email to the user"},
                status=status.HTTP_400_BAD_REQUEST
            )

    # delete account
    def delete(self, request):
        pass



class ProductView(APIView):

    permission_classes = [permissions.AllowAny]
    
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

