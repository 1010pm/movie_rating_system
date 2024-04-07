from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


class Movie(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField(null=True, blank=True)
    main_cast = models.CharField(max_length=255, null=True, blank=True)
    director = models.CharField(max_length=255, null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

# class User(models.Model):
#     username = models.CharField(max_length=255)
#     password = models.CharField(max_length=255)

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 11)])

class Memory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    date = models.DateField()
    photos = models.ImageField(upload_to='memory_photos/')
    story = models.TextField()

class Photo(models.Model):
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='photos/')

class Star(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    stars = models.IntegerField()
