# Generated by Django 2.0 on 2018-10-24 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0002_profil'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profil',
            name='favorites',
            field=models.TextField(default='[]', null=True),
        ),
    ]