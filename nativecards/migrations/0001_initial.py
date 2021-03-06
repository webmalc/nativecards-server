# Generated by Django 2.1 on 2018-08-24 10:18

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('is_enabled', models.BooleanField(db_index=True, default=True, verbose_name='is enabled')),
                ('attempts_to_remeber', models.PositiveIntegerField(default=10, help_text='number of correct answers to remember the card', validators=[django.core.validators.MinValueValidator(3), django.core.validators.MaxValueValidator(50)], verbose_name='attempts to remeber')),
                ('cards_per_lesson', models.PositiveIntegerField(default=10, help_text='number of cards to study per the lesson', validators=[django.core.validators.MinValueValidator(5), django.core.validators.MaxValueValidator(50)], verbose_name='cards per lesson')),
                ('cards_to_repeat', models.PositiveIntegerField(default=5, help_text='number of cards to repeat per the lesson', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(50)], verbose_name='cards to repeat')),
                ('lesson_latest_days', models.PositiveIntegerField(default=21, help_text='number of days for getting the latest added cards', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(50)], verbose_name='lesson latest days')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nativecards_settings_created_by', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nativecards_settings_modified_by', to=settings.AUTH_USER_MODEL, verbose_name='modified by')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
