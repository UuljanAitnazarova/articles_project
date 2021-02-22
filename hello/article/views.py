from django.shortcuts import render

from article.models import Article


def index_view(request):
    """
    Представление для отображения списка статей
    """
    articles = Article.objects.all()  # Получаем список статей из базы данных
    return render(request, 'index.html', context={'articles': articles})  # Возвращаем "скомпилированный" шаблон с использованием переданного списка статей


def home_view(request):
    return render(request, 'home.html')


def article_create_view(request):
    if request.method == "GET":
        return render(request, 'article_create.html')
    elif request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        author = request.POST.get("author")

        article = Article.objects.create(
            title=title,
            content=content,
            author=author
        )

        return render(request, 'home.html')