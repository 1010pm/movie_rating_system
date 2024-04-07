from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path("<int:movie_pk>/rate/", MovieRatingView.as_view()),
    path("all/", GetAllMovies.as_view()),
    path("<int:movie_pk>/details/", MovieDetailAPIView.as_view()),
    path("movies/search/", MovieSearchAPIView.as_view(), name="movie_search"),
    path("top-rated-movies/", TopRatedMoviesAPIView.as_view(), name="top_rated"),
    path("movie/compare/", CompareRatingsAPIView.as_view()),

    path("memory/create-memory/", CreateMemoryAPIView.as_view(), name="create_memory"),
    path("memory/my-memories/", MyMemoriesAPIView.as_view(), name="my_memories"),
    path("memory/<int:id>/", MemoryDetailAPIView.as_view(), name="memory_detail"),
    path("memory/<int:memory_id>/photo/", MemoryPhotoAPIView.as_view(), name="memory_photo"),
    path("memory/update/<int:pk>/", UpdateMemoryAPIView.as_view(), name="update_memory"),
    path("memory/delete/<int:pk>/", DeleteMemoryAPIView.as_view(), name="delete_memory"),

    path("memory/top-words/", TopWordsAPIView.as_view(), name="top_words"),
    path("memory/<int:memory_id>/urls/", ExtractURLsAPIView.as_view(), name="extract_urls"),

    path("guess-movie/", GuessMovieAPIView.as_view(), name="guess_movie"),
]
