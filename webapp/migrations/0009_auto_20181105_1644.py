# Generated by Django 2.0 on 2018-11-05 15:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0008_auto_20181104_2146'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='search',
            name='API_KEY',
        ),
        migrations.RemoveField(
            model_name='search',
            name='query',
        ),
    ]
