from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
import json

from django.views.decorators.csrf import ensure_csrf_cookie

from article.models import Article

# Create your views here.
def product_list_view(request, *args, **kwargs):
    if request.method == 'GET':
        fields = ['id', 'title', 'content']
        articles = Article.objects.values(*fields)
        return JsonResponse(list(articles), safe=False)


def product_create_view(request, *args, **kwargs):
    if request.method == 'POST':
        if request.body:

            article_data = json.loads(request.body)
            article = Article.objects.create(**article_data)
            return JsonResponse({'id': article.pk})
        else:
            response = JsonResponse({'error': 'No data provided!'})
            response.status_code = 400
            return response

@ensure_csrf_cookie
def get_token_view(request, *args, **kwargs):
    if request.method == 'GET':
        return HttpResponse()
    return HttpResponseNotAllowed('Only GET request are allowed')