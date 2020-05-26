# Generated by Django 3.0 on 2020-05-26 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0026_artist_last_changed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Search',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField(choices=[('album', 'Album'), ('artist', 'Artist'), ('genre', 'Genre'), ('song', 'Song'), ('tag', 'Tag')], help_text='The model that is being searched.', max_length=100, verbose_name='model')),
                ('field', models.CharField(help_text='The field to search for', max_length=255, verbose_name='search field')),
                ('type', models.CharField(choices=[('contains', 'Contains'), ('icontains', 'Case-insensitive Contains'), ('exact', 'Exact'), ('iexact', 'Case-insensitive Exact')], help_text='The type of search to execute. See the docs for information on how each works.', max_length=100, verbose_name='search type')),
                ('active', models.BooleanField(default=True, help_text='Enables/disables the search field.', verbose_name='active')),
                ('description', models.TextField(blank=True, help_text='Human-readable explanation of the search field', null=True, verbose_name='description')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('last_changed', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'search field',
                'verbose_name_plural': 'search fields',
            },
        ),
        migrations.CreateModel(
            name='AlbumSearch',
            fields=[
            ],
            options={
                'verbose_name': 'album search field',
                'verbose_name_plural': 'album search fields',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('content.search',),
        ),
        migrations.CreateModel(
            name='ArtistSearch',
            fields=[
            ],
            options={
                'verbose_name': 'artist search field',
                'verbose_name_plural': 'artist search fields',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('content.search',),
        ),
        migrations.CreateModel(
            name='GenreSearch',
            fields=[
            ],
            options={
                'verbose_name': 'genre search field',
                'verbose_name_plural': 'genre search fields',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('content.search',),
        ),
        migrations.CreateModel(
            name='SongSearch',
            fields=[
            ],
            options={
                'verbose_name': 'song search field',
                'verbose_name_plural': 'song search fields',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('content.search',),
        ),
        migrations.CreateModel(
            name='TagSearch',
            fields=[
            ],
            options={
                'verbose_name': 'tag search field',
                'verbose_name_plural': 'tag search fields',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('content.search',),
        ),
    ]
