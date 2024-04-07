import json
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.dateparse import parse_date
from ...models import Movie
from ...serializers import MovieSerializer
import requests


class Command(BaseCommand):
    help = 'Loads movies from a JSON file into the database, fetching additional details from an API.'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file containing movie data.')

    def handle(self, *args, **options):
        json_file = options['json_file']
        with open(json_file, 'r') as f:
            movie_data = json.load(f)

        for movie in movie_data:
            # Extract movie ID from the current data
            movie_id = movie.get('id') 
            if movie_id:
                try:
                    # Fetch additional details from the API
                    api_url = f'https://cinema.stag.rihal.tech/api/movie/{movie_id}'
                    response = requests.get(api_url)
                    response.raise_for_status()  # Raise an exception for non-200 status codes
                    api_data = response.json()

                    # Convert release date format
                    release_date = parse_date(api_data['release_date'])
                    api_data['release_date'] = release_date

                    # Convert main cast list to string
                    main_cast = ', '.join(api_data.get('main_cast', []))
                    api_data['main_cast'] = main_cast

                    # Combine data from JSON and API
                    combined_data = {**movie, **api_data}

                    # Serialize and save the movie data
                    serializer = MovieSerializer(data=combined_data)
                    if serializer.is_valid():
                        with transaction.atomic():
                            serializer.save()
                    else:
                        self.stdout.write(self.style.ERROR(f"Error creating movie (ID: {movie_id}): {serializer.errors}"))
                except requests.RequestException as e:
                    self.stdout.write(self.style.ERROR(f"Error fetching API data for movie ID {movie_id}: {e}"))
            else:
                self.stdout.write(self.style.WARNING("Skipping movie entry: Missing ID"))
