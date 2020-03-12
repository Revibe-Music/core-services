# Generated by Django 3.0 on 2020-03-12 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_customuser_programmatic_account'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='programmatic_account',
            field=models.BooleanField(blank=True, default=False, help_text='Programmatic accounts cannot login by normal means, they can only have access token generated for use in supplemental applications', null=True, verbose_name='programmatic account'),
        ),
    ]
