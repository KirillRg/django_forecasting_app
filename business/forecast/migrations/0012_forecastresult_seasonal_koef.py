# Generated by Django 5.0.4 on 2024-05-09 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0011_alter_coherenceindicator_indicator_value_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='forecastresult',
            name='seasonal_koef',
            field=models.FloatField(default=0.5, verbose_name='Расичтанный коэфицицент сезонности'),
        ),
    ]
