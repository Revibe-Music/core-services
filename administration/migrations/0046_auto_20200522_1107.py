# Generated by Django 3.0 on 2020-05-22 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0045_blog_last_changed'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='last_changed',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
