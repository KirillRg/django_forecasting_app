# Generated by Django 5.0.4 on 2024-05-03 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0005_alter_forecastdata_period_month'),
    ]

    operations = [
        migrations.AddField(
            model_name='forecastdata',
            name='seasonal_level',
            field=models.FloatField(default=0.5, verbose_name='Сезонные колебания'),
        ),
    ]
