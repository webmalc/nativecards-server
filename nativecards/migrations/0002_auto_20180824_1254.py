# Generated by Django 2.1 on 2018-08-24 12:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nativecards', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='settings',
            options={'ordering': ['-created'], 'verbose_name_plural': 'settings'},
        ),
        migrations.RemoveField(
            model_name='settings',
            name='attempts_to_remeber',
        ),
        migrations.AddField(
            model_name='settings',
            name='attempts_to_remember',
            field=models.PositiveIntegerField(default=10, help_text='number of correct answers to remember the card', validators=[django.core.validators.MinValueValidator(3), django.core.validators.MaxValueValidator(50)], verbose_name='attempts to remember'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='lesson_latest_days',
            field=models.PositiveIntegerField(default=21, help_text='number of days for getting the latest added cards', validators=[django.core.validators.MinValueValidator(5), django.core.validators.MaxValueValidator(50)], verbose_name='lesson latest days'),
        ),
    ]