# Generated by Django 2.1 on 2018-10-03 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nativecards', '0005_auto_20181003_1340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='play_audio_on_open',
            field=models.BooleanField(db_index=True, default=True, help_text='play an audio when the card is opening', verbose_name='play audio on open'),
        ),
    ]