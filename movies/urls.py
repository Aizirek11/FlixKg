from django.urls import path
from .views import (
    MovieListView, MovieDetailView, MovieCreateView, MovieUpdateDeleteView,
    ActorListCreateView, ActorDetailView, GenreListCreateView, ReviewListCreateView
)

urlpatterns = [
    # Фильмы
    path('movies/', MovieListView.as_view(), name='movie-list'),
    path('movies/manage/', MovieCreateView.as_view(), name='movie-create'),
    path('movies/<int:pk>/', MovieDetailView.as_view(), name='movie-detail'),
    path('movies/<int:pk>/manage/', MovieUpdateDeleteView.as_view(), name='movie-update'),
    path('movies/<int:pk>/reviews/', ReviewListCreateView.as_view(), name='movie-reviews'),

    # Актёры
    path('actors/', ActorListCreateView.as_view(), name='actor-list'),
    path('actors/<int:pk>/', ActorDetailView.as_view(), name='actor-detail'),

    # Жанры
    path('genres/', GenreListCreateView.as_view(), name='genre-list'),
]