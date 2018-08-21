# Generated by Django 2.1 on 2018-08-21 08:51

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0004_auto_20180821_0721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='complete',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='complete'),
        ),
        migrations.AlterField(
            model_name='card',
            name='deck',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cards', to='cards.Deck', verbose_name='deck'),
        ),
        migrations.AlterField(
            model_name='card',
            name='examples',
            field=models.TextField(blank=True, db_index=True, null=True, validators=[django.core.validators.MinLengthValidator(2)], verbose_name='examples'),
        ),
    ]
