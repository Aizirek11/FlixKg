from django.contrib import admin
from django.contrib import admin
from .models import Movie, Actor, Genre, MovieActor, Review


class MovieActorInline(admin.TabularInline):
    model = MovieActor
    extra = 1


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_year', 'duration', 'age_limit']
    search_fields = ['title']
    inlines = [MovieActorInline]


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'rating', 'created_at']
# Register your models here.
