from django.shortcuts import render
from articles.models import Article


def articles_list(request):
    template = 'articles/news.html'
    context = {}
    # используйте этот параметр для упорядочивания результатов
    # https://docs.djangoproject.com/en/3.1/ref/models/querysets/#django.db.models.query.QuerySet.order_by
    ordering = '-published_at'
    context['object_list'] = Article.objects.prefetch_related('scopes').order_by(ordering).all()
    return render(request, template, context)
