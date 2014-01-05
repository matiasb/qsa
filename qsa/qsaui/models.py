from django.db import models


class Series(models.Model):

    name = models.TextField()
    overview = models.TextField()
    first_aired = models.DateField()
    runtime = models.PositiveIntegerField()  # minutes
    tags = models.TextField()
    cast = models.TextField()
    poster = models.URLField()
    completed = models.BooleanField(default=False)
    tvdb_id = models.CharField(max_length=256)
    imdb_id = models.CharField(max_length=256)


class Season(models.Model):

    series = models.ForeignKey(Series)
    year = models.PositiveIntegerField(null=True)
    number = models.PositiveIntegerField()


class Episode(models.Model):

    season = models.ForeignKey(Season)
    number = models.PositiveIntegerField()
    name = models.TextField()
    overview = models.TextField()
    first_aired = models.DateField()
    image = models.URLField()
    tvdb_id = models.CharField(max_length=256)
    imdb_id = models.CharField(max_length=256)
    writer = models.TextField(null=True)
    director = models.TextField(null=True)
