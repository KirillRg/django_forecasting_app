from django.db import models

class ForecastData(models.Model):
    net_profit = models.TextField(verbose_name='Чистая прибыль', default='0')
    profitability = models.TextField(verbose_name='Рентабельность', default='0')
    operating_expenses = models.TextField(verbose_name='Операционные расходы', default='0')
    customer_base = models.TextField(verbose_name='Клиентская база', default='0')
    employee_count = models.TextField(verbose_name='Количество сотрудников', default='0')
    period_month = models.IntegerField(verbose_name='Период месяца')
    seasonal_level = models.FloatField(verbose_name='Сезонные колебания', default=0.5)
    artefact = models.TextField(verbose_name='Главный бизнес-артефакт', default='')
    month = models.TextField(verbose_name='Месяц прогноза', default='')

    def __str__(self):
        return f"Forecast Data for {self.period_month} months"
    def parse_float_list(self, data_str):
        """ Парсит строку с данными, разделёнными запятой, и возвращает список чисел. """
        numbers = []
        try:
            if data_str:
                numbers = [float(num) for num in data_str.split(',')]
        except ValueError:
            pass  # Можно добавить логирование ошибки
        return numbers

    def get_net_profit(self):
        return self.parse_float_list(self.net_profit)

    def get_profitability(self):
        return self.parse_float_list(self.profitability)

    def get_operating_expenses(self):
        return self.parse_float_list(self.operating_expenses)

    def get_customer_base(self):
        return self.parse_float_list(self.customer_base)

    def get_employee_count(self):
        return self.parse_float_list(self.employee_count)

class BusinessIndicator(models.Model):
    indicator_value = models.FloatField(verbose_name='Значение индикатора')
    param = models.CharField(max_length=100, verbose_name='Для показателя')
    forecast_data = models.ForeignKey(ForecastData, on_delete=models.CASCADE, related_name='indicators')

    class Meta:
        abstract = True

class SeasonalityIndicator(BusinessIndicator):
    forecast_data = models.ForeignKey(ForecastData, on_delete=models.CASCADE, related_name='seasonality_indicators')
class GrowthStabilityIndicator(BusinessIndicator):
    forecast_data = models.ForeignKey(ForecastData, on_delete=models.CASCADE, related_name='growth_stability_indicators')
class CoherenceIndicator(BusinessIndicator):
    forecast_data = models.ForeignKey(ForecastData, on_delete=models.CASCADE, related_name='coherence_indicators')
class DynamicsIndicator(BusinessIndicator):
    forecast_data = models.ForeignKey(ForecastData, on_delete=models.CASCADE, related_name='dynamics_indicators')

class ForecastResult(models.Model):
    forecast_data = models.OneToOneField(ForecastData, on_delete=models.CASCADE, related_name='result')
    success_probability = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Вероятность успеха')
    result_comment = models.TextField(verbose_name='Комментарий к результату')
    seasonal_koef = models.FloatField(verbose_name='Расичтанный коэфицицент сезонности', default=0.0)

    def __str__(self):
        return f"Forecast Result for {self.forecast_data.period_month}"
