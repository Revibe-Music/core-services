# Generated by Django 3.0 on 2020-05-27 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer_success', '0009_auto_20200527_1212'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='required_request_body_kwargs',
            field=models.TextField(default='{}', help_text='Keyword arguments that must evaludate to True when checked against the request parameter arguments. Must use JSON encoding.', verbose_name='request body kwargs'),
        ),
    ]
