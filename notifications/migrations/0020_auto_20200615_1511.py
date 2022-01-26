# Generated by Django 3.0 on 2020-06-15 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0019_notification_date_seen'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationtemplate',
            name='branch_campaign',
            field=models.CharField(blank=True, help_text='Branch campaign/what?', max_length=255, null=True, verbose_name='campaign'),
        ),
        migrations.AddField(
            model_name='notificationtemplate',
            name='branch_channel',
            field=models.CharField(blank=True, help_text='Branch channel/source', max_length=255, null=True, verbose_name='channel'),
        ),
        migrations.AddField(
            model_name='notificationtemplate',
            name='branch_tags',
            field=models.TextField(blank=True, help_text='Comma-separated tags for branch links', null=True, verbose_name='tags'),
        ),
    ]