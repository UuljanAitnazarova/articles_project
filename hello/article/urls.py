from django.urls import path

from article.views import (
    IndexView,
    ArticleView,
    CreateArticleView,
    ArticleUpdateView,
    ArticleCommentCreate,
    ArticleDeleteView,
    ArticleLikeView,
    ArticleLikeRemoveView,
    CommentLikeView,
    CommentRemoveView,
)


app_name = 'article'

urlpatterns = [
    path('', IndexView.as_view(), name='list'),
    path('add/', CreateArticleView.as_view(), name='add'),
    path('<int:pk>/', ArticleView.as_view(), name='view'),
    path('<int:pk>/like', ArticleLikeView.as_view(), name='like'),
    path('comments/<int:pk>/like', CommentLikeView.as_view(), name='comment-like'),
    path('comments/<int:pk>/unlike', CommentRemoveView.as_view(), name='comment-unlike'),
    path('<int:pk>/unlike', ArticleLikeRemoveView.as_view(), name='unlike'),
    path('<int:pk>/update', ArticleUpdateView.as_view(), name='update'),
    path('<int:pk>/delete', ArticleDeleteView.as_view(), name='delete'),
    path('<int:pk>/comments/add/', ArticleCommentCreate.as_view(), name='comment-create')
]
