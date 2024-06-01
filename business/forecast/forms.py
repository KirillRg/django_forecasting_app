from django import forms
from .models import ForecastData

class MonthSelectionForm(forms.Form):
    MONTH_CHOICES = [
        ('Январь', 'Январь'), ('Февраль', 'Февраль'), ('Март', 'Март'), ('Апрель', 'Апрель'),
        ('Май', 'Май'), ('Июнь', 'Июнь'), ('Июль', 'Июль'), ('Август', 'Август'),
        ('Сентябрь', 'Сентябрь'), ('Октябрь', 'Октябрь'), ('Ноябрь', 'Ноябрь'), ('Декабрь', 'Декабрь')
    ]
    month = forms.ChoiceField(choices=MONTH_CHOICES, label="Месяц для прогноза эффективности")
    period_month = forms.IntegerField(min_value=3, max_value=12, label="Количество месяцев для ввода")
    seasonal_level = forms.FloatField(
        widget=forms.NumberInput(attrs={'type': 'range', 'min': '0.1', 'max': '0.9', 'step': '0.1'}),
        min_value=0.1,
        max_value=0.9,
        label="Уровень сезонных колебаний")
    artefact = forms.Field(label="Главный бизнес-артефакт")

class ForecastDataForm(forms.ModelForm):
    class Meta:
        model = ForecastData
        fields = ['net_profit', 'profitability', 'operating_expenses', 'customer_base', 'employee_count']