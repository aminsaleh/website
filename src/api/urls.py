from django.urls import path

from .views import *


urlpatterns = [
    # path('accounts', UserView.as_view()),
    path('accounts/getInfo', UserView.as_view(http_method_names=['get'])),
    path('accounts/register', UserView.as_view(http_method_names=['post'])),
    path('accounts/confirm', UserView.as_view(http_method_names=['get'])),
    path('accounts/update', UserView.as_view(http_method_names=['put'])),
    path('accounts/forgetPassword', UserView.as_view(http_method_names=['patch'])),

    # path('products', ProductView.as_view()),
    path('products/getAll', ProductView.as_view(http_method_names=['get'])),
    path('products/getById', ProductView.as_view(http_method_names=['post'])),

    # path('order', OrderView.as_view())
]
