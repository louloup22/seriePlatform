# Generated by Django 2.0 on 2018-10-27 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0003_auto_20181024_1410'),
    ]

    operations = [
        migrations.AddField(
            model_name='serie',
            name='alert',
            field=models.IntegerField(default=None, verbose_name='Days before next episode'),
        ),
        migrations.AddField(
            model_name='serie',
            name='poster_path',
            field=models.CharField(max_length=200, null=True, verbose_name='Poster path'),
        ),
        migrations.AddField(
            model_name='serie',
            name='seasons',
            field=models.TextField(null=True, verbose_name='Seasons and episodes info'),
        ),
        migrations.AddField(
            model_name='serie',
            name='serie_id',
            field=models.IntegerField(default=999999999, verbose_name='Serie id'),
        ),
        migrations.AddField(
            model_name='serie',
            name='video',
            field=models.CharField(max_length=200, null=True, verbose_name='Video path'),
        ),
        migrations.AddField(
            model_name='serie',
            name='video_title',
            field=models.CharField(max_length=200, null=True, verbose_name='Video title'),
        ),
        migrations.AlterField(
            model_name='profil',
            name='favorites',
            field=models.TextField(blank=True, default='[]', null=True),
        ),
        migrations.AlterField(
            model_name='serie',
            name='genres',
            field=models.TextField(null=True),
        ),
    ]
