# Generated by Django 2.2.7 on 2019-12-04 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0019_auto_20191203_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='category',
            field=models.CharField(blank=True, choices=[('word', 'word'), ('phrase', 'phrase'), ('phrasal_verb', 'phrasal verb')], db_index=True, max_length=30, null=True, verbose_name='category'),
        ),
    ]
