# Generated by Django 2.1 on 2018-10-03 09:17

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cards', '0012_auto_20181003_0902'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='card',
            unique_together={('word', 'created_by')},
        ),
        migrations.AlterUniqueTogether(
            name='deck',
            unique_together={('title', 'created_by')},
        ),
    ]