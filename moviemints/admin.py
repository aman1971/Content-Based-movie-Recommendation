from django.contrib import admin
from .models import MovieData, MovieIndices

# Register your models here.
admin.site.register(MovieData)
admin.site.register(MovieIndices)