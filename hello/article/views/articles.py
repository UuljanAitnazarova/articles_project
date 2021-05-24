from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView, TemplateView
)
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.utils.http import urlencode

from article.models import Article, Comment, ArticleLikes, CommentLikes
from article.forms import ArticleForm, SearchForm


class IndexView(ListView):
    """
    Представление для просмотра списка статей. Представление реализовано с
    использованием generic-представления ListView.

    В представлении активирована пагинация и реализован поиск
    """
    template_name = 'articles/index.html'
    model = Article
    context_object_name = 'articles'
    ordering = ('title', '-created_at')
    paginate_by = 5
    paginate_orphans = 1

    def get(self, request, **kwargs):
        self.form = SearchForm(request.GET)
        self.search_data = self.get_search_data()
        return super(IndexView, self).get(request, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.search_data:
            queryset = queryset.filter(
                Q(title__icontains=self.search_data) |
                Q(author__icontains=self.search_data) |
                Q(content__icontains=self.search_data)
            )
        return queryset

    def get_search_data(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search_value']
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.form

        if self.search_data:
            context['query'] = urlencode({'search_value': self.search_data})

        try:
            article_likes = ArticleLikes.objects.filter(user=self.request.user)
            liked_articles = []
            for a in article_likes:
                liked_articles.append(a.article.pk)
            context['liked_articles'] = liked_articles

            comment_likes = CommentLikes.objects.filter(user=self.request.user)
            liked_comments = []
            for c in comment_likes:
                liked_comments.append(c.comment.pk)
            context['liked_comments'] = liked_comments
        except TypeError:
            pass

        return context


class ArticleView(DetailView):
    model = Article
    template_name = 'articles/view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            article = self.object
            article_likes = ArticleLikes.objects.filter(user=self.request.user)
            liked_articles = []
            for a in article_likes:
                liked_articles.append(a.article.pk)
            context['liked_articles'] = liked_articles

            comment_likes = CommentLikes.objects.filter(user=self.request.user)
            liked_comments = []
            for c in comment_likes:
                liked_comments.append(c.comment.pk)
            context['liked_comments'] = liked_comments
        except TypeError:
            pass
        return context


class CreateArticleView(PermissionRequiredMixin, CreateView):
    template_name = 'articles/create.html'
    form_class = ArticleForm
    model = Article
    success_url = reverse_lazy('article:list')
    permission_required = 'article.add_article'

    def form_valid(self, form):
        tags = form.cleaned_data.pop('tags')

        article = form.save(commit=False)
        article.author = self.request.user
        article.save()

        article.tags.set(tags)
        return redirect(self.get_success_url())


class ArticleUpdateView(PermissionRequiredMixin, UpdateView):
    form_class = ArticleForm
    model = Article
    template_name = 'articles/update.html'
    context_object_name = 'article'
    permission_required = 'article.change_article'

    def has_permission(self):
        return self.get_object().author == self.request.user or super().has_permission()

    def get_success_url(self):
        return reverse('article:view', kwargs={'pk': self.kwargs.get('pk')})


class ArticleDeleteView(PermissionRequiredMixin, DeleteView):
    model = Article
    template_name = 'articles/delete.html'
    context_object_name = 'article'
    success_url = reverse_lazy('article:list')
    permission_required = 'article.delete_article'


class ArticleLikeView(LoginRequiredMixin, TemplateView):
    template_name = 'articles/view.html'

    def get(self, request, *args, **kwargs):
        self.article = Article.objects.get(pk=self.kwargs.get('pk'))
        user = self.request.user
        try:
            article_like = ArticleLikes.objects.get(article=self.article, user=user)
            HttpResponseForbidden()
        except ArticleLikes.DoesNotExist:
            ArticleLikes.objects.create(user=user, article=self.article)

        return HttpResponse(self.article.article_likes.count())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['article'] = self.article
        return context


class ArticleLikeRemoveView(LoginRequiredMixin, TemplateView):
    template_name = 'articles/view.html'

    def get(self, request, *args, **kwargs):
        self.article = Article.objects.get(pk=self.kwargs.get('pk'))
        user = self.request.user
        try:
            article_like = ArticleLikes.objects.get(article=self.article, user=user)
            article_like.delete()
        except ArticleLikes.DoesNotExist:
            HttpResponseForbidden()
        print(self.article.article_likes.count())
        return HttpResponse(self.article.article_likes.count())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['article'] = self.article
        return context


class CommentLikeView(LoginRequiredMixin, TemplateView):
    pass
    template_name = 'articles/view.html'

    def get(self, request, *args, **kwargs):
        self.comment = Comment.objects.get(pk=self.kwargs.get('pk'))
        user = self.request.user
        try:
            comment_like = CommentLikes.objects.get(comment=self.comment, user=user)
            HttpResponseForbidden()
        except CommentLikes.DoesNotExist:
            CommentLikes.objects.create(user=user, comment=self.comment)
        return HttpResponse(self.comment.likes.count())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = self.comment
        return context


class CommentRemoveView(LoginRequiredMixin, TemplateView):
    pass
    template_name = 'articles/view.html'

    def get(self, request, *args, **kwargs):
        self.comment = Comment.objects.get(pk=self.kwargs.get('pk'))
        user = self.request.user
        try:
            comment_like = CommentLikes.objects.get(comment=self.comment, user=user)
            comment_like.delete()
        except CommentLikes.DoesNotExist:
            pass
        return HttpResponse(self.comment.likes.count())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = self.comment
        return context
