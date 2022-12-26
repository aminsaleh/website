from django.urls import path

from .views import *


urlpatterns = [
    # accounts
    path('accounts/getInfo', UserView.as_view(http_method_names=['get']), name="account_info_page"),
    path('accounts/register', UserView.as_view(http_method_names=['post']), name='register_page'),
    path('accounts/confirm', UserView.as_view(http_method_names=['get']), name='confirm_page'),
    path('accounts/update', UserView.as_view(http_method_names=['patch'])),
    path(
        'accounts/forgetPassword',
        UserView.as_view(http_method_names=['get', 'post', 'patch']),
        name='forget_password',
    ),

    # products
    path('products/getAll', ProductView.as_view(http_method_names=['post'])),
    path('products/getByCode', ProductView.as_view(http_method_names=['post'])),

    # order
    path('order/addProduct', OrderView.as_view(http_method_names=['post'])),
    path('order/removeProduct', OrderView.as_view(http_method_names=['post'])),
    path('order/basketView', OrderView.as_view(http_method_names=['post'])),
    path('order/checkoutOrder', OrderView.as_view(http_method_names=['post'])),
    path('order/paymentRedirect', OrderView.as_view(http_method_names=['post'])),
]
