# Generated by Django 2.1.2 on 2018-10-25 12:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nativecards', '0009_auto_20181021_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='lessons_per_day',
            field=models.PositiveIntegerField(default=2, help_text='number of lessons to complete per day', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(50)], verbose_name='lessons per day'),
        ),
    ]
