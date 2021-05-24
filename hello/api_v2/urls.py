from django.contrib import admin
from django.urls import path, include

from api_v2.views import ArticleListView, ArticleDetailView

app_name = 'api_v2'

urlpatterns = [
    path('', ArticleListView.as_view(), name='list'),
    path('<int:pk>/', ArticleDetailView.as_view(), name='detail'),

]