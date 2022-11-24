# Generated by Django 4.0 on 2022-08-10 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MovieData',
            fields=[
                ('movie_id', models.IntegerField(primary_key=True, serialize=False)),
                ('movie_imdb_id', models.ImageField(upload_to='')),
                ('movie_name', models.CharField(max_length=200)),
                ('language', models.CharField(max_length=100)),
                ('overview', models.TextField()),
                ('release_date', models.DateField(blank=True)),
                ('status', models.CharField(max_length=50)),
                ('rating', models.FloatField()),
                ('vote_count', models.IntegerField()),
                ('genre', models.CharField(max_length=200)),
                ('runtime', models.IntegerField()),
                ('poster_url', models.URLField()),
            ],
        ),
    ]