# Generated by Django 3.0 on 2020-03-23 19:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0024_blog_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blogtag',
            options={'verbose_name': 'blog tag', 'verbose_name_plural': 'blog tags'},
        ),
    ]
