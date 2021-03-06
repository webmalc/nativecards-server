# Generated by Django 2.2.8 on 2019-12-18 13:08

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import markdownx.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('is_enabled', models.BooleanField(db_index=True, default=True, verbose_name='is enabled')),
                ('word', models.CharField(db_index=True, max_length=255, validators=[django.core.validators.MinLengthValidator(2)], verbose_name='word')),
                ('category', models.CharField(blank=True, choices=[('word', 'word'), ('phrase', 'phrase'), ('phrasal_verb', 'phrasal verb')], db_index=True, max_length=30, null=True, verbose_name='category')),
                ('definition', markdownx.models.MarkdownxField(blank=True, db_index=True, null=True, validators=[django.core.validators.MinLengthValidator(2)], verbose_name='definition')),
                ('examples', markdownx.models.MarkdownxField(blank=True, db_index=True, null=True, validators=[django.core.validators.MinLengthValidator(2)], verbose_name='examples')),
                ('synonyms', markdownx.models.MarkdownxField(blank=True, db_index=True, null=True, validators=[django.core.validators.MinLengthValidator(2)], verbose_name='synonyms')),
                ('antonyms', markdownx.models.MarkdownxField(blank=True, db_index=True, null=True, validators=[django.core.validators.MinLengthValidator(2)], verbose_name='antonyms')),
                ('transcription', models.CharField(blank=True, db_index=True, max_length=255, null=True, validators=[django.core.validators.MinLengthValidator(2)], verbose_name='transcription')),
                ('pronunciation', models.URLField(blank=True, null=True, verbose_name='pronunciation')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='words_word_created_by', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='words_word_modified_by', to=settings.AUTH_USER_MODEL, verbose_name='modified by')),
            ],
            options={
                'ordering': ('word',),
                'unique_together': {('word',)},
            },
        ),
    ]
