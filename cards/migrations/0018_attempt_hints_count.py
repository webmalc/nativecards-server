# Generated by Django 2.2.7 on 2019-11-28 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0017_auto_20181011_1003'),
    ]

    operations = [
        migrations.AddField(
            model_name='attempt',
            name='hints_count',
            field=models.PositiveIntegerField(db_index=True, default=0, verbose_name='hints count'),
        ),
    ]