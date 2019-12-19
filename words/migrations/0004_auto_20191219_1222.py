# Generated by Django 2.2.8 on 2019-12-19 12:22

import django.contrib.postgres.fields.hstore
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('words', '0003_auto_20191219_1034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='word',
            name='translations',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, db_index=True, default=dict, null=True, verbose_name='translations'),
        ),
    ]
