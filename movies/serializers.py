from rest_framework import serializers
from .models import Movie, Actor, Genre, MovieActor, Review


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['id', 'name', 'photo', 'bio']


class MovieActorSerializer(serializers.ModelSerializer):
    actor = ActorSerializer()

    class Meta:
        model = MovieActor
        fields = ['actor', 'role']


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'text', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Оценка должна быть от 1 до 5!')
        return value


class MovieListSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = ['id', 'title', 'poster', 'genre', 'duration', 'age_limit', 'release_year', 'average_rating']

    def get_average_rating(self, obj):
        return obj.average_rating()


class MovieDetailSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    movie_actors = MovieActorSerializer(many=True)
    reviews = ReviewSerializer(many=True)
    average_rating = serializers.SerializerMethodField()
    trailer_embed = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'poster', 'trailer_url', 'trailer_embed',
                  'genre', 'duration', 'age_limit', 'release_year',
                  'movie_actors', 'reviews', 'average_rating']

    def get_average_rating(self, obj):
        return obj.average_rating()

    def get_trailer_embed(self, obj):
        if obj.trailer_url:
            video_id = obj.trailer_url.split('v=')[-1].split('&')[0]
            return f'https://www.youtube.com/embed/{video_id}'
        return None


class MovieCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'