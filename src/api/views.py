from types import SimpleNamespace

from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.db.models import Q
from loguru import logger
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.config.mail import Mail

from .models import *
from .serializers import *


class CostumePermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        authentication_reqs = ['GET','PUT','PATCH','DELETE']
        requset_method = request.method
        user_authenticated = request.user.is_authenticated

        if requset_method=='POST':
            return True
        if (
            requset_method=='GET' 
            and request.path_info==reverse('confirm_page')
        ):
            return True
        if (requset_method in authentication_reqs) and (user_authenticated):
            return True
            
        return False


class UserView(APIView):

    # permission_classes = [CostumePermissions]
    permission_classes = [permissions.AllowAny]

    # getInfo
    def get(self, request):

        # request.session
        
        url_path = request.path_info

        if url_path==reverse('account_info_page'):
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
                    {'message': 'User Not Found :('},
                    status=status.HTTP_404_NOT_FOUND
                )

        if url_path==reverse('confirm_page'):
            uidb64 = request.GET['uidb64']
            token = request.GET['token']
            if uidb64 is not None and token is not None:
                uid = urlsafe_base64_decode(uidb64)
                user = User.objects.get(pk=uid)
                token_exist = default_token_generator.check_token(user, token)
                
                if token_exist and not user.is_confirmed:
                    logger.info(f'{token_exist}, type{type(token_exist)}')
                    user.is_confirmed = True
                    user.save()
                    return Response(
                        {"status": "user confirmed :)"},
                        status=status.HTTP_200_OK
                    )

                elif user.is_confirmed:
                    return Response(
                        {
                            "status": {
                                "user_confirmed": True,
                            }
                        },
                        status=status.HTTP_200_OK
                    )

                else:
                    # if not send another token email to the user
                    return Response(
                        {"status":"email not confirmed :("},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        if url_path==reverse('forget_password'):
            uidb64 = request.GET['uidb64']
            token = request.GET['token']
            if uidb64 is not None and token is not None:
                uid = urlsafe_base64_decode(uidb64)
                user = User.objects.get(pk=uid)
                token_exist = default_token_generator.check_token(user, token)
                
                if token_exist:
                    logger.info(f'{token_exist}, type{type(token_exist)}')
                    
                    return Response(
                        {"status": "show password reset form :)"},
                        status=status.HTTP_200_OK
                    )

    # register
    def post(self, request):
        
        url_path = request.path_info

        if url_path==reverse('register_page'):
            if request.data['password']!=request.data['confirm_password']:
                return Response(
                    {"status": "Mismatch passwords :("},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.create(serializer.validated_data)
                return Response(
                    data=serializer.data,
                    status=status.HTTP_201_CREATED
                )

            
            try:
                send_mail = Mail(user=user, url=reverse('confirm_page'))
                send_mail()
                
                return Response(
                    {"status": "user registered :)"},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {"status": "there was a problem in sending email :("},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if url_path==reverse('forget_password'):
            username_or_email = request.data['forget_info']
            user = User.objects.get(Q(username=username_or_email) | Q(email=username_or_email))
            mail = Mail(user=user, url=reverse('forget_password'))
            mail()
            return Response(
                {"status": "please check your email :)"},
                status=status.HTTP_200_OK
            )


    # update
    def patch(self, request):

        # request.session
        user = User.objects.get(username=request.user.username)
        if request.data['password']!=request.data['confirm_password']:
            return Response(
                {"status": "Mismatch passwords :("},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        modification_data = {}
        for key in request.data:
            if request.data[key]!=user.__dict__[key]:
                modification_data[key] = request.data[key]
        
        serializer = UserSerializer(data=modification_data, partial=True)
        if serializer.is_valid():
            user = serializer.update(
                instance=user,
                validated_data=serializer.validated_data
            )
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error_fields": serializer.errors.keys()},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    # delete account
    def delete(self, request):
        # check for the two factor authentication
        # and then delete the user
        # or even make it in the 20 days period
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
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'status': 'there is no products here :('},
                status=status.HTTP_404_NOT_FOUND
            )


    # ProductGetByCode
    def post(self, request):
    
        product_code = request.data["product_code"]
        product = Product.objects.get(code=product_code)
        serializer = serializer = ProductSerializer(product)
        if product:
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'status':'there is no such a product :('},
                status=status.HTTP_404_NOT_FOUND
            )


class OrderView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        
        request_path = request.path_info

        if request_path=='/order/addProduct':
            # check if there is a product like this one
            # add a row to the orders if there is not
            # increase the number of purchased if there is

            product_info = {
                "product_code": request.data["product_code"],
                "user": request.user,
            }

            product_query = Order.objects.filter(
                user=user,
                selected_product=Product.objects.filter(code=product_info["product_code"]),
            )

            if product_query > 0:
                try:
                    product_query.product_count += 1
                    product_query.save()
                    return Response(
                        {'status':'product count increased :)'},
                        status=status.HTTP_200_OK
                    )
                except Exception as e:
                    return Response(
                        {"status": "product count not increased :("},
                        status=status.HTTP_304_NOT_MODIFIED
                    )
            else:
                try:
                    order = Order.objects.create(
                        status='bs',
                        # purchase_time=,
                        # deliver_time=,
                        user=product_info["user"],
                        selected_product=product_query,
                        product_count=1,
                        # order_id=hash of user and product and count,
                        post_method=0,
                        post_id='',
                        payment_method=0,
                        payment_status='',
                    )
                    order.save()
                    return Response(
                        {'status':'product added :)'},
                        status=status.HTTP_200_OK
                    )
                except Exception as e:
                    return Response(
                        {"status": "product not added :("},
                        status=status.HTTP_304_NOT_MODIFIED
                    )


        if request_path=='/order/removeProduct':
            # find the row for this product
            # decrease the number of purchased
            # if its zero remove the row

            product_info = {
                "product_code": request.data["product_code"],
                "user": request.user,
            }
            
            product_query = Order.objects.filter(
                user=user,
                selected_product=Product.objects.filter(code=product_info["product_code"]),
            )

            if product_query.product_count>1:
                try:
                    product_query.product_count -= 1
                    product_query.save()
                    return Response(
                        {'status':'product count decresed :)'},
                        status=status.HTTP_200_OK
                    )
                except Exception as e:
                    return Response(
                        {'status':'product count not decresed :('},
                        status=status.HTTP_304_NOT_MODIFIED
                    )

            else:
                try:
                    product_query.delete()
                    return Response(
                        {'status':'product deleted :)'},
                        status=status.HTTP_200_OK
                    )
                except Exception as e:
                    return Response(
                        {'status':'product not deleted :('},
                        status=status.HTTP_304_NOT_MODIFIED
                    )


        if request_path=='/order/basketView':
            # get the user correspondig order's products
            # and show them in the left side of the main page

            user = request.user

            try:
                products_query = Order.objects.filter(
                    status='bs',
                    user=user,
                )

                # do some calculations here
                # like, sum of all products values, ... 

                serializer = OrderSerializer(products_query)
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'status':'no products found :('},
                    status=status.HTTP_404_NOT_FOUND
                )


        if request_path=='/order/checkoutOrder':
            # check the view page {1,2,3,4}
            # page number 1: show correspondig products, that can be edited
            # page number 2: show the user info, that can be edited
            # page number 3: show the post method and payment method and redirect link to the payment
            # page number 4: show the status of order: user info, post info, payment info
            # in every view check the necessary information that should be completed
            
            user = request.user
            try:
                view_page = request.data['view_page']
            except Exception as e:
                view_page = 1
            
            if view_page==1:

                try:
                    products_query = Order.objects.filter(
                        status='bs',
                        user=user,
                    )

                    # calculations can done here

                    serializer = OrderSerializer(products_query)
                    return Response(
                        serializer.data,
                        status=status.HTTP_200_OK
                    )
                except Exception as e:
                    return Response(
                        {'status':'no products found :('},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            if view_page==2:

                # check if previous sections' data provided completely
                # nothin to check here :)

                try:
                    user_query = User.objects.filter(
                        user=user,
                    )

                    serializer = UserSerializer(user_query)
                    return Response(
                        serializer.data,
                        status=status.HTTP_200_OK
                    )
                except Exception as e:
                    return Response(
                        {'status':'user not found :('},
                        status=status.HTTP_404_NOT_FOUND
                    )                
            
            if view_page==3:

                # check if previous sections' data provided completely
                if request.data["user_check"]:
                    pass

                # make models for post and payment methods
                # and their corresponing data like tokens, ...
                
                # post_methods = Post.objects.all()
                # post_serializer = serializers(post_methods)
                
                # payment_methods = Payment.objects.all()
                # payment_serializer = serializers(payment_methods)
                
                # return Response(
                #     {
                #         'post_methods': post_serializer.data,
                #         'payment_methods': payment_serializer.data,
                #     },
                #     status=status.HTTP_200_OK
                # )

                pass
            
            if view_page==4:

                # check if previous sections' data provided completely
                # set the post_method and payment_method in the products 
                # then forward to the payment process
                # redirect to the success page

                pass
            

        if request_path=='/order/paymentRedirect':
            
            # redirect from the banking process
            # on success! set the post_id, payment_status, status in order's products

            pass

        


