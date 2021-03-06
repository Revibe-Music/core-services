# Generated by Django 3.0 on 2020-06-18 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0023_notificationtemplate_render_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationtemplate',
            name='render_version',
            field=models.CharField(blank=True, choices=[('v1', 'Simple Python Rendering (V1)'), ('v2', 'Django Template Rendering (V2)')], default='v2', help_text='Version of HTML rendering to use when formatting the message.', max_length=255, verbose_name='render version'),
        ),
    ]
