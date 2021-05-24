from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinLengthValidator
from django.conf import settings


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Article(BaseModel):
    title = models.CharField(
        max_length=120,
        null=False,
        blank=False,
        verbose_name='Заголовок',
        validators=(MinLengthValidator(5),)
    )
    content = models.TextField(max_length=3000, null=False, blank=False, verbose_name='Контент')
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles'
    )
    tags = models.ManyToManyField(
        'article.Tag',
        related_name='articles',
        db_table='article_tags'
    )

    class Meta:
        db_table = 'articles'
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        permissions = [
            ('сan_have_piece_of_pizza', 'Может съесть кусочек пиццы')
        ]

    def __str__(self):
        return f'{self.id}. {self.author}: {self.title}'


class Comment(BaseModel):
    article = models.ForeignKey(
        'article.Article',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Статья',
        null=False,
        blank=False
    )
    comment = models.CharField(max_length=200, verbose_name='Комментарий', null=False, blank=False)
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name='comments'
    )

    class Meta:
        db_table = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
    
    def __str__(self):
        return f'{self.author}: {self.comment}'


class Tag(BaseModel):
    tag = models.CharField(max_length=200, verbose_name='Тэг')

    class Meta:
        db_table = 'tags'
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
    
    def __str__(self):
        return self.tag


class ArticleLikes(BaseModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='article_likes')
    article = models.ForeignKey('article.Article', on_delete=models.CASCADE, related_name='article_likes')

    class Meta:
        db_table = 'article_likes'
        verbose_name = 'Лайк статьи'
        verbose_name_plural = 'Лайки статей'

    def __str__(self):
        return f'{self.user} - {self.article}'



class CommentLikes(BaseModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='likes')
    comment = models.ForeignKey('article.Comment', on_delete=models.CASCADE, related_name='likes')

    class Meta:
        db_table = 'comment_likes'
        verbose_name = 'Лайк комментария'
        verbose_name_plural = 'Лайки комментариев'

    def __str__(self):
        return f'{self.user} - {self.comment}'