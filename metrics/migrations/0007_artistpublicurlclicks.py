# Generated by Django 3.0 on 2020-04-01 19:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0019_auto_20200330_1100'),
        ('metrics', '0006_auto_20200303_1552'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArtistPublicURLClicks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('artist', models.ForeignKey(blank=True, help_text='Artist whose page was clicked on', limit_choices_to={'platform': 'Revibe'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='url_clicks', to='content.Artist', verbose_name='artist')),
            ],
            options={
                'verbose_name': 'artist public URL click',
                'verbose_name_plural': 'artist public URL clicks',
            },
        ),
    ]
