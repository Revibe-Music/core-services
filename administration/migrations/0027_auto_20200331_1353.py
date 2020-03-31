# Generated by Django 3.0 on 2020-03-31 18:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0019_auto_20200330_1100'),
        ('administration', '0026_auto_20200325_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='artist',
            field=models.ForeignKey(blank=True, help_text="Artist related to the blog post, like an 'Artist of the Week'-type post.", limit_choices_to={'platform': 'Revibe'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='blogs_single', to='content.Artist', verbose_name='artist'),
        ),
        migrations.AddField(
            model_name='blog',
            name='artists',
            field=models.ManyToManyField(blank=True, help_text='Artists related to the blog post, like weekly featured artists or something like that.', limit_choices_to={'platform': 'Revibe'}, related_name='blogs_multiple', to='content.Artist', verbose_name='artists'),
        ),
    ]
