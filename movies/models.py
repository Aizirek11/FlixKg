from django.db import models
from users.models import User
import re


class Genre(models.Model):
    name = models.CharField(max_length=100, verbose_name='Жанр')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Actor(models.Model):
    name = models.CharField(max_length=200, verbose_name='Имя актёра')
    photo = models.ImageField(upload_to='actors/', blank=True, null=True, verbose_name='Фото')
    bio = models.TextField(blank=True, verbose_name='Биография')

    class Meta:
        verbose_name = 'Актёр'
        verbose_name_plural = 'Актёры'

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    poster = models.ImageField(upload_to='posters/', blank=True, null=True, verbose_name='Постер')
    trailer_url = models.URLField(blank=True, verbose_name='Ссылка на трейлер YouTube')
    genre = models.ManyToManyField(Genre, verbose_name='Жанр')
    duration = models.PositiveIntegerField(verbose_name='Длительность (мин)')
    age_limit = models.CharField(max_length=10, verbose_name='Возрастной рейтинг')
    release_year = models.PositiveIntegerField(verbose_name='Год выхода')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'

    def __str__(self):
        return self.title

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    @property
    def trailer_embed(self):
        if not self.trailer_url:
            return None
        match = re.search(r'(?:v=|youtu\.be/|embed/)([a-zA-Z0-9_-]{11})', self.trailer_url)
        if match:
            return f'https://www.youtube.com/embed/{match.group(1)}'
        return None


class MovieActor(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_actors')
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    role = models.CharField(max_length=200, verbose_name='Роль в фильме')

    class Meta:
        verbose_name = 'Актёр в фильме'
        verbose_name_plural = 'Актёры в фильме'

    def __str__(self):
        return f'{self.actor.name} — {self.role}'


class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        verbose_name='Оценка'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.user.username} — {self.movie.title} ({self.rating}⭐)'