from rest_framework import serializers
from .models import Movie, User, Rating, Memory, Photo, Star
from django.contrib.humanize.templatetags.humanize import intcomma

from rest_framework import serializers
from .models import Movie, Rating

class MovieSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = ['id', 'name', 'description', 'average_rating']

    def get_average_rating(self, obj):
        ratings = Rating.objects.filter(movie=obj)
        if ratings.exists():
            total_ratings = sum(rating.value for rating in ratings)
            return total_ratings / ratings.count()
        return 0

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        max_length = 100
        if len(representation['description']) > max_length:
            representation['description'] = representation['description'][:max_length]
            representation['description'] = representation['description'][:representation['description'].rfind(' ')]
            representation['description'] += '...'
        return representation


class MovieDetailSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    budget_in_english = serializers.SerializerMethodField()
    your_rating = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = ['id', 'name', 'description', 'release_date', 'main_cast', 'director', 'budget', 'budget_in_english', 'average_rating', 'your_rating']

    def get_average_rating(self, obj):
        ratings = Rating.objects.filter(movie=obj)
        if ratings.exists():
            total_ratings = sum(rating.value for rating in ratings)
            return total_ratings / ratings.count()
        return 0  # Or any default value you want

    def get_your_rating(self, obj):
        return 0  # Default value for your rating if not available

    def get_budget_in_english(self, obj):
        budget = obj.budget
        if budget is not None:
            return intcomma(budget)  # Convert to comma-separated number
        return "Unknown"  # Or any default value for unknown budget


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'


class MemorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Memory
        fields = ['title', 'date', 'photos', 'story']


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'


class StarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Star
        fields = '__all__'
