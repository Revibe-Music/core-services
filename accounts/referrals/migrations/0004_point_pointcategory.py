# Generated by Django 3.0 on 2020-06-04 17:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('referrals', '0003_auto_20200603_1308'),
    ]

    operations = [
        migrations.CreateModel(
            name='PointCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name')),
                ('points', models.IntegerField(default=0, help_text='The number of points to be assigned for a referred user taking this action', verbose_name='points')),
                ('active', models.BooleanField(default=True, help_text='This category will be used to assign points to users', verbose_name='active')),
                ('description', models.TextField(blank=True, help_text='Human-readable information about this category', null=True, verbose_name='description')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('last_changed', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField(help_text='The change in points for this user', verbose_name='points')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_points', to='referrals.PointCategory', verbose_name='category')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='points', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'point',
                'verbose_name_plural': 'points',
            },
        ),
    ]
