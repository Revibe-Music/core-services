# Generated by Django 3.0 on 2020-02-07 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0008_auto_20200205_1120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactform',
            name='email',
            field=models.CharField(blank=True, help_text='Email', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='contactform',
            name='first_name',
            field=models.CharField(blank=True, help_text='First Name', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='contactform',
            name='last_name',
            field=models.CharField(blank=True, help_text='Last Name', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='contactform',
            name='message',
            field=models.TextField(help_text='Message'),
        ),
        migrations.AlterField(
            model_name='contactform',
            name='subject',
            field=models.CharField(blank=True, help_text='Contact form subject / type of request', max_length=255, null=True),
        ),
    ]
