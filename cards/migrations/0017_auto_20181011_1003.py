# Generated by Django 2.1.2 on 2018-10-11 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0016_auto_20181003_0948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attempt',
            name='form',
            field=models.CharField(choices=[('listen', 'listen'), ('write', 'write'), ('speak', 'speak')], db_index=True, max_length=30, verbose_name='form'),
        ),
    ]
