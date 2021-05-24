from django.contrib import admin
from django.urls import path, include

from api.views import product_list_view, product_create_view, get_token_view


urlpatterns = [
    path('', product_list_view, name='list-view'),
    path('create/', product_create_view),
    path('get_token/', get_token_view),
]