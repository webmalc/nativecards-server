# Generated by Django 2.1 on 2018-08-21 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0003_auto_20180820_1043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='pronunciation',
            field=models.URLField(blank=True, null=True, verbose_name='pronunciation'),
        ),
    ]
