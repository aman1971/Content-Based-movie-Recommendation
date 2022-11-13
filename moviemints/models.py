from re import M
from django.db import models

# Create your models here.
class MovieData(models.Model):
    def __str__(self):
        return self.movie_name

    movie_id = models.IntegerField(primary_key=True)
    movie_imdb_id = models.CharField(max_length=100)
    movie_name = models.CharField(max_length=200)
    language = models.CharField(max_length=100)
    overview = models.TextField()
    release_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50)
    rating = models.FloatField()
    vote_count = models.IntegerField()
    genre = models.CharField(max_length=200)
    runtime = models.IntegerField()
    poster_url = models.URLField(max_length=200)



class MovieIndices(models.Model):
    def __str__(self):
        return self.movie_index

    movie_index = models.IntegerField(primary_key=True)
    movie = models.ForeignKey(MovieData, on_delete=models.CASCADE)
    movie_name = models.CharField(max_length=200)

    @property
    def movie_name(self):
        return self.movie.movie_name
