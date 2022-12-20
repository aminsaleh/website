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
                    {'message': 'User Not Found :('},
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
                            {"status":"user confirmed :)"},
                            status=status.HTTP_200_OK
                        )
                except:
                    # if not send another token email to the user
                    return Response(
                        {"status":"email not confirmed :("},
                        status=status.HTTP_400_BAD_REQUEST
                    )                    

        else:
            # useless code!
            return Response(
                {"status":"url not found :("},
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
                {"status":"Empty Password :("},
                status=status.HTTP_400_BAD_REQUEST
            )

        if account_info['password']!=account_info['confirm_password']:
            return Response(
                {"status":"Mismatch passwords :("},
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
                {"status": "username or email is not unique :("},
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

            logger.info(uid)
            logger.info(token)

            send_mail(subject, html_content, email_from, recipient_list)

            return Response(
                {"status": "user registered :)"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"status":"there was a problem in sending email :("},
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
            user = User.objects.get(username=request.user)    
        except Exception as e:
            return Response(
                {"status":"user not found :("},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            user.first_name=account_info['first_name']
            user.last_name=account_info['last_name']
            user.email=account_info['email']
            user.username=account_info['username']
            user.phone=account_info['phone']
            user.address=account_info['address']
            user.birthday=account_info['birthday']
            user.is_confirmed=False
            user.save()
            
        except Exception as e:
            return Response(
                {"status":"updating user unsuccessfull :("},
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
                {"status":"user updated :)"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status":"there was a problem in sending email :("},
                status=status.HTTP_400_BAD_REQUEST
            )


    # forget
    def patch(self, request):

        # request.session

        account_info = {
            "old_password": request.data['old_password'],
            "new_password": request.data['new_password'],
            "confirm_new_password": request.data['confirm_new_password'],
        }

        # check passwords
        try:
            user = User.objects.get(username=request.user)        
        except Exception as e:
            return Response(
                {"status":"user not found :("},
                status=status.HTTP_404_NOT_FOUND
            )

        if not account_info['old_password'] and \
            not account_info['new_password'] or \
            not account_info['confirm_new_password']:
            return Response(
                {"status":"Empty Password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if account_info['new_password']!=account_info['confirm_new_password']:
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
                {"status":"updating user unsuccessfull :("},
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
                {"status":"user updated :)"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status":"there was a problem in sending email :("},
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
            user = request.user
            product_code = request["product_code"]

            product_query = Order.objects.filter(
                user=user,
                selected_product=Product.objects.filter(code=product_code),
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
                        user=request.user,
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
            user = request.user
            product_code = request["product_code"]

            product_query = Order.objects.filter(
                user=user,
                selected_product=Product.objects.filter(code=product_code),
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
                    #product_query.product_count==0
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

        


