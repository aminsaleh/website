from django.urls import path

from .views import *


urlpatterns = [
    # path('accounts', UserView.as_view()),
    path('accounts/getInfo', UserView.as_view(http_method_names=['get'])),
    path('accounts/register', UserView.as_view(http_method_names=['post'])),
    path('accounts/confirm', UserView.as_view(http_method_names=['post'])),
    path('accounts/update', UserView.as_view(http_method_names=['put'])),
    path('accounts/forgetPassword', UserView.as_view(http_method_names=['patch'])),

    # path('products', ProductView.as_view()),
    path('product/getAll', ProductView.as_view(http_method_names=['get'])),
    path('product/getById', ProductView.as_view(http_method_names=['post'])),

    # path('order', OrderView.as_view())
]
