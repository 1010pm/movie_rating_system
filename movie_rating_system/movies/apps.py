from django.apps import AppConfig
from django.conf import settings
import os

from django.db.models.signals import post_migrate

def load_movies(sender, **kwargs):
    from .models import Movie
    if sender.name == 'movies' and not Movie.objects.exists():
        json_file_path = os.path.join(settings.BASE_DIR, 'movies', 'movies_data', 'movies.json')
        from django.core.management import call_command
        call_command('load_movies', json_file_path)

class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movies'

    def ready(self):
        post_migrate.connect(load_movies, sender=self)
  