# Generated by Django 2.0 on 2018-11-04 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0005_serie_favorites_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serie',
            name='alert',
            field=models.IntegerField(default=999999, null=True, verbose_name='Days before next episode'),
        ),
    ]
