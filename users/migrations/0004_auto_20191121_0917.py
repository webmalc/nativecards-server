# Generated by Django 2.2.7 on 2019-11-21 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20181106_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='verification_code',
            field=models.CharField(blank=True, db_index=True, max_length=200, null=True, unique=True),
        ),
    ]
