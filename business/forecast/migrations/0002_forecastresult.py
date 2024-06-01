# Generated by Django 5.0.4 on 2024-04-25 17:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForecastResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('success_probability', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Вероятность успеха')),
                ('result_comment', models.TextField(verbose_name='Комментарий к результату')),
                ('forecast_data', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='result', to='forecast.forecastdata')),
            ],
        ),
    ]