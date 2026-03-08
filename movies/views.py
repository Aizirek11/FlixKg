from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from rest_framework import generics, permissions, filters
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Movie, Actor, Genre, Review
from .serializers import (
    MovieListSerializer, MovieDetailSerializer, MovieCreateSerializer,
    ActorSerializer, GenreSerializer, ReviewSerializer
)


class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'genre__name']


class MovieDetailView(generics.RetrieveAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieDetailSerializer
    permission_classes = [permissions.AllowAny]


class MovieCreateView(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class MovieUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class ActorListCreateView(generics.ListCreateAPIView):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = [permissions.IsAdminUser]


class ActorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = [permissions.IsAdminUser]


class GenreListCreateView(generics.ListCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.IsAdminUser]


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(movie_id=self.kwargs['pk'])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, movie_id=self.kwargs['pk'])


def movie_list_view(request):
    movies = Movie.objects.all()
    genres = Genre.objects.all()

    search = request.GET.get('search')
    if search:
        movies = movies.filter(title__icontains=search)

    genre_id = request.GET.get('genre')
    if genre_id:
        movies = movies.filter(genre__id=genre_id)

    paginator = Paginator(movies, 8)
    page = request.GET.get('page')
    movies = paginator.get_page(page)

    return render(request, 'movies/movie_list.html', {
        'movies': movies,
        'genres': genres,
    })


def movie_detail_view(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    sessions = movie.sessions.all().order_by('date', 'start_time')
    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'sessions': sessions,
    })


@login_required
def add_review_view(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        text = request.POST.get('text')
        if rating and text:
            Review.objects.create(
                movie=movie,
                user=request.user,
                rating=int(rating),
                text=text
            )
            messages.success(request, 'Отзыв добавлен!')
    return redirect(f'/movies/{pk}/')




@staff_member_required
def admin_panel_view(request):
    from bookings.models import Hall, Session
    movies = Movie.objects.all()
    actors = Actor.objects.all()
    genres = Genre.objects.all()
    halls = Hall.objects.all()
    sessions = Session.objects.all().order_by('-date')
    return render(request, 'movies/admin_panel.html', {
        'movies': movies,
        'actors': actors,
        'genres': genres,
        'halls': halls,
        'sessions': sessions,
    })


@staff_member_required
def add_movie_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        release_year = request.POST.get('release_year')
        duration = request.POST.get('duration')
        age_limit = request.POST.get('age_limit')
        trailer_url = request.POST.get('trailer_url', '')
        genre_ids = request.POST.getlist('genre')
        poster = request.FILES.get('poster')

        movie = Movie.objects.create(
            title=title,
            description=description,
            release_year=release_year,
            duration=duration,
            age_limit=age_limit,
            trailer_url=trailer_url,
            poster=poster
        )
        movie.genre.set(genre_ids)
        messages.success(request, f'Фильм "{title}" добавлен!')
    return redirect('/admin-panel/')


@staff_member_required
def delete_movie_view(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    movie.delete()
    messages.success(request, 'Фильм удалён!')
    return redirect('/admin-panel/')


@staff_member_required
def add_actor_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        bio = request.POST.get('bio', '')
        photo = request.FILES.get('photo')
        Actor.objects.create(name=name, bio=bio, photo=photo)
        messages.success(request, f'Актёр "{name}" добавлен!')
    return redirect('/admin-panel/')


@staff_member_required
def delete_actor_view(request, pk):
    actor = get_object_or_404(Actor, pk=pk)
    actor.delete()
    messages.success(request, 'Актёр удалён!')
    return redirect('/admin-panel/')


@staff_member_required
def add_session_view(request):
    from bookings.models import Hall, Session
    if request.method == 'POST':
        movie_id = request.POST.get('movie')
        hall_id = request.POST.get('hall')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        price_standard = request.POST.get('price_standard')
        price_vip = request.POST.get('price_vip')

        Session.objects.create(
            movie_id=movie_id,
            hall_id=hall_id,
            date=date,
            start_time=start_time,
            price_standard=price_standard,
            price_vip=price_vip
        )
        messages.success(request, 'Сеанс добавлен!')
    return redirect('/admin-panel/')


@staff_member_required
def delete_session_view(request, pk):
    from bookings.models import Session
    session = get_object_or_404(Session, pk=pk)
    session.delete()
    messages.success(request, 'Сеанс удалён!')
    return redirect('/admin-panel/')

@staff_member_required
def add_hall_view(request):
    from bookings.models import Hall, Seat
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address', '')
        total_rows = int(request.POST.get('total_rows'))
        total_seats = int(request.POST.get('total_seats'))
        vip_rows = int(request.POST.get('vip_rows', 0))

        hall = Hall.objects.create(
            name=name,
            address=address,
            total_rows=total_rows,
            total_seats=total_seats
        )

        # Автоматически создаём все места
        for row in range(1, total_rows + 1):
            for seat_num in range(1, total_seats + 1):
                seat_type = 'vip' if row <= vip_rows else 'standard'
                Seat.objects.create(
                    hall=hall,
                    row=row,
                    number=seat_num,
                    seat_type=seat_type
                )

        messages.success(request, f'Зал "{name}" добавлен с {total_rows * total_seats} местами!')
    return redirect('/admin-panel/')

@staff_member_required
def edit_movie_view(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    genres = Genre.objects.all()
    if request.method == 'POST':
        movie.title = request.POST.get('title')
        movie.description = request.POST.get('description')
        movie.release_year = request.POST.get('release_year')
        movie.duration = request.POST.get('duration')
        movie.age_limit = request.POST.get('age_limit')
        movie.trailer_url = request.POST.get('trailer_url', '')
        genre_ids = request.POST.getlist('genre')
        if request.FILES.get('poster'):
            movie.poster = request.FILES.get('poster')
        movie.save()
        movie.genre.set(genre_ids)
        messages.success(request, f'Фильм "{movie.title}" обновлён!')
        return redirect('/admin-panel/')
    return render(request, 'movies/edit_movie.html', {
        'movie': movie,
        'genres': genres,
    })


@staff_member_required
def add_movie_actor_view(request):
    from .models import MovieActor
    if request.method == 'POST':
        movie_id = request.POST.get('movie')
        actor_id = request.POST.get('actor')
        role = request.POST.get('role', '')
        MovieActor.objects.create(movie_id=movie_id, actor_id=actor_id, role=role)
        messages.success(request, 'Актёр добавлен в фильм!')
    return redirect('/admin-panel/')

@staff_member_required
def delete_movie_actor_view(request, pk):
    from .models import MovieActor
    ma = get_object_or_404(MovieActor, pk=pk)
    ma.delete()
    messages.success(request, 'Актёр удалён из фильма!')
    return redirect('/admin-panel/')