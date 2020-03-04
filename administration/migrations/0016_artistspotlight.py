# Generated by Django 3.0 on 2020-03-02 22:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0014_auto_20200226_1026'),
        ('administration', '0015_auto_20200228_1637'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArtistSpotlight',
            fields=[
                ('date', models.DateField(primary_key=True, serialize=False)),
                ('artist', models.ForeignKey(help_text='Artist to spotlight on the Revibe Music home screen', limit_choices_to={'platform': 'Revibe'}, on_delete=django.db.models.deletion.CASCADE, related_name='spotlights', to='content.Artist', verbose_name='artist')),
            ],
            options={
                'verbose_name': ('artist spotlight',),
                'verbose_name_plural': 'artist spotlights',
            },
        ),
    ]