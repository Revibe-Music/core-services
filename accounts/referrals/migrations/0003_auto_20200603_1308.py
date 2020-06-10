# Generated by Django 3.0 on 2020-06-03 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('referrals', '0002_auto_20200603_1307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referral',
            name='referree_ip_address',
            field=models.CharField(blank=True, help_text='The IP address of the referree. Used for scam prevention', max_length=255, null=True, verbose_name='referred IP address'),
        ),
    ]