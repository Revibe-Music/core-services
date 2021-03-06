# Generated by Django 3.0 on 2020-05-20 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0014_externalevent'),
        ('customer_success', '0003_action_extra_events'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='extra_events',
            field=models.ManyToManyField(blank=True, help_text='Additional, attribution-only events. These are External Events that prompt the user to perform this action.', related_name='action_prompts', to='notifications.ExternalEvent', verbose_name='extra events'),
        ),
    ]
