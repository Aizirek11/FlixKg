from django.shortcuts import render, get_object_or_404
from .models import News

def news_list_view(request):
    news = News.objects.filter(is_published=True)
    return render(request, 'news/news_list.html', {'news': news})

def news_detail_view(request, pk):
    item = get_object_or_404(News, pk=pk, is_published=True)
    return render(request, 'news/news_detail.html', {'item': item})