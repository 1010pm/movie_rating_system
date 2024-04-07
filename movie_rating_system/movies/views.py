from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from .models import Movie, User, Rating, Memory, Photo, Star
from .serializers import (
    MovieSerializer, UserSerializer, RatingSerializer, MemorySerializer,
    PhotoSerializer, StarSerializer, MovieDetailSerializer
)
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
import re
from collections import Counter
from django.db.models import Avg
from django.db.models.functions import Length


class UserRegistrationAPIView(APIView):
    """
    API endpoint to register a user into the system.
    """
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from rest_framework_simplejwt.tokens import RefreshToken

class LoginAPIView(APIView):
    """
    API endpoint to authenticate users.
    """
    def get(self,request):
         return Response({'error': 'get not aloud'}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Generate access and refresh tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({'access_token': access_token}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



class MovieListAPIView(APIView):
    """
    API endpoint to retrieve all movies.
    """
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        movies = Movie.objects.all()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)


class MovieRatingView(APIView):
    """
    API endpoint to rate a movie.
    """
    def post(self, request, movie_pk):
        try:
            movie = Movie.objects.get(pk=movie_pk)
            rating_value = int(request.data.get('rating'))
            if 1 <= rating_value <= 10:
                user_id = request.user.id  # Assuming user is authenticated
                rating, created = Rating.objects.update_or_create(
                    user_id=user_id,
                    movie_id=movie_pk,
                    defaults={'rating': rating_value}
                )
                return Response({'message': 'Movie rated successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Invalid rating value. Rating must be between 1 and 10'},
                                status=status.HTTP_400_BAD_REQUEST)
        except Movie.DoesNotExist:
            return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)


class GetAllMovies(APIView):
    """
    API endpoint to retrieve all movies.
    """
    def get(self, request):
        movies = Movie.objects.all()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)


class MovieDetailAPIView(APIView):
    """
    API endpoint to retrieve details of a movie.
    """
    def get(self, request, movie_pk):
        try:
            movie = Movie.objects.get(pk=movie_pk)
            serializer = MovieDetailSerializer(movie)
            return Response(serializer.data)
        except Movie.DoesNotExist:
            return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)


class MovieSearchAPIView(APIView):
    """
    API endpoint to search movies.
    """
    def get(self, request):
        search_param = request.query_params.get('search')
        if not search_param:
            return Response({'message': 'Please provide a search parameter'}, status=status.HTTP_400_BAD_REQUEST)

        movies = Movie.objects.filter(name__icontains=search_param) | Movie.objects.filter(
            description__icontains=search_param)
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)


class TopRatedMoviesAPIView(APIView):
    """
    API endpoint to retrieve top-rated movies.
    """
    def get(self, request):
        top_rated_movies = Movie.objects.annotate(avg_rating=Avg('rating__value')).order_by('-avg_rating')[:5]
        serializer = MovieSerializer(top_rated_movies, many=True)
        return Response(serializer.data)


class CompareRatingsAPIView(APIView):
    """
    API endpoint to compare user ratings with average ratings.
    """
    def get(self, request):
        user_ratings = Rating.objects.filter(user=request.user)
        average_ratings = Rating.objects.annotate(avg_rating=Avg('rating')).values('movie', 'avg_rating')
        max_ratings = []
        for rating in user_ratings:
            movie_id = rating.movie.id
            user_rating = rating.rating
            avg_rating = average_ratings.filter(movie=movie_id).first().get('avg_rating', 0)
            is_user_rating_max = user_rating >= avg_rating
            max_ratings.append({
                'id': movie_id,
                'name': rating.movie.name,
                'rating': user_rating,
                'is_user_rating_max': is_user_rating_max
            })
        return Response(max_ratings)


class CreateMemoryAPIView(APIView):
    """
    API endpoint to create a memory.
    """
    def get(self, request):
        memories = Memory.objects.filter(user=request.user)
        serializer = MemorySerializer(memories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MemorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyMemoriesAPIView(APIView):
    """
    API endpoint to retrieve memories of the authenticated user.
    """
    def get(self, request):
        memories = Memory.objects.filter(user=request.user)
        serializer = MemorySerializer(memories, many=True)
        return Response(serializer.data)


class MemoryDetailAPIView(APIView):
    """
    API endpoint to retrieve details of a memory.
    """
    def get(self, request, id):
        try:
            memory = Memory.objects.get(pk=id)
            serializer = MemorySerializer(memory)
            return Response(serializer.data)
        except Memory.DoesNotExist:
            return Response({'error': 'Memory not found'}, status=status.HTTP_404_NOT_FOUND)


class MemoryPhotoAPIView(APIView):
    """
    API endpoint to retrieve photos of a memory.
    """
    def get(self, request, memory_id):
        try:
            memory = Memory.objects.get(pk=memory_id)
            photos = memory.photos.all()
            serializer = PhotoSerializer(photos, many=True)
            return Response(serializer.data)
        except Memory.DoesNotExist:
            return Response({'error': 'Memory not found'}, status=status.HTTP_404_NOT_FOUND)


class UpdateMemoryAPIView(APIView):
    """
    API endpoint to update a memory.
    """
    def put(self, request, pk):
        try:
            memory = Memory.objects.get(pk=pk)
            serializer = MemorySerializer(memory, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Memory.DoesNotExist:
            return Response({'error': 'Memory not found'}, status=status.HTTP_404_NOT_FOUND)


class DeleteMemoryAPIView(APIView):
    """
    API endpoint to delete a memory.
    """
    def delete(self, request, pk):
        try:
            memory = Memory.objects.get(pk=pk)
            memory.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Memory.DoesNotExist:
            return Response({'error': 'Memory not found'}, status=status.HTTP_404_NOT_FOUND)


class TopWordsAPIView(APIView):
    """
    API endpoint to retrieve top used words in memories.
    """
    def get(self, request):
        memories = Memory.objects.all()
        all_words = [word.lower() for memory in memories for word in re.findall(r'\w+', memory.story)]
        word_count = Counter(all_words)
        top_words = word_count.most_common(10)
        return Response({'top_words': top_words})


class ExtractURLsAPIView(APIView):
    """
    API endpoint to extract URLs from a memory.
    """
    def get(self, request, memory_id):
        try:
            memory = Memory.objects.get(pk=memory_id)
            urls = re.findall(
                r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                memory.story)
            return Response({'urls': urls})
        except Memory.DoesNotExist:
            return Response({'error': 'Memory not found'}, status=status.HTTP_404_NOT_FOUND)


class GuessMovieAPIView(APIView):
    """
    API endpoint to guess a movie from a scrambled name.
    """
    def get(self, request):
        # Implement your code for guessing a movie from a scrambled name here
        # This is just a placeholder, you'll need to replace it with your actual implementation
        return Response({'message': 'Movie guessed successfully'}, status=status.HTTP_200_OK)
