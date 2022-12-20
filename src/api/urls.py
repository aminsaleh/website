from django.urls import path

from .views import *


urlpatterns = [
    # accounts
    path('accounts/getInfo', UserView.as_view(http_method_names=['get'])),
    path('accounts/register', UserView.as_view(http_method_names=['post'])),
    path('accounts/confirm', UserView.as_view(http_method_names=['get'])),
    path('accounts/update', UserView.as_view(http_method_names=['put'])),
    path('accounts/forgetPassword', UserView.as_view(http_method_names=['patch'])),

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
