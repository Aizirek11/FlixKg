from django.urls import path
from .views import news_list_view, news_detail_view

urlpatterns = [
    path('news/', news_list_view, name='news-list'),
    path('news/<int:pk>/', news_detail_view, name='news-detail'),
]