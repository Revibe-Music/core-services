# Generated by Django 3.0 on 2020-04-22 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0021_auto_20200421_1014'),
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(help_text='The genre itself', max_length=255, verbose_name='text')),
            ],
        ),
        migrations.RemoveField(
            model_name='song',
            name='genre',
        ),
        migrations.AddField(
            model_name='album',
            name='genres',
            field=models.ManyToManyField(blank=True, related_name='albums', to='content.Genre'),
        ),
        migrations.AddField(
            model_name='song',
            name='genres',
            field=models.ManyToManyField(blank=True, related_name='songs', to='content.Genre'),
        ),
    ]
