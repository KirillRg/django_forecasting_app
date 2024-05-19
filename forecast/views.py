from django.shortcuts import render, redirect
from .forms import MonthSelectionForm, ForecastDataForm
from .models import ForecastData, ForecastResult, SeasonalityIndicator, GrowthStabilityIndicator, DynamicsIndicator, CoherenceIndicator
import datetime
import calendar
from pytrends.request import TrendReq
import time

def main_view(request):
    if request.method == 'POST':
        form = MonthSelectionForm(request.POST)
        if form.is_valid():
            request.session['month'] = form.cleaned_data['month']
            request.session['period_month'] = form.cleaned_data['period_month']
            request.session['seasonal_level'] = form.cleaned_data['seasonal_level']
            request.session['artefact'] = form.cleaned_data['artefact']
            return redirect('forecast_view')
    else:
        form = MonthSelectionForm()

    results = ForecastResult.objects.all()

    return render(request, 'forecast/main.html', {'form': form, 'results': results})

#Главная форма
def forecast_view(request):
    month = request.session.get('month', 'Январь')
    period_month = request.session.get('period_month', 3)
    seasonal_level = request.session.get('seasonal_level', 0.5)
    artefact = request.session.get('artefact', '')

    if request.method == 'POST':
        # Получаем данные из формы для каждого месяца и объединяем их в одну строку
        combined_data = {}
        for i in range(1, period_month + 1):
            net_profit = request.POST.getlist(f"net_profit_{i}")
            profitability = request.POST.getlist(f"profitability_{i}")
            operating_expenses = request.POST.getlist(f"operating_expenses_{i}")
            customer_base = request.POST.getlist(f"customer_base_{i}")
            employee_count = request.POST.getlist(f"employee_count_{i}")

            combined_data[i] = "|".join(
                [",".join(net_profit), ",".join(profitability), ",".join(operating_expenses), ",".join(customer_base),
                 ",".join(employee_count)])

        # Создаем объект модели ForecastData с объединенными данными
        forecast_data = ForecastData.objects.create(period_month=period_month, seasonal_level=seasonal_level,
                                                    artefact=artefact, month=month)

        # Создаем списки для каждого поля
        net_profit_list = []
        profitability_list = []
        operating_expenses_list = []
        customer_base_list = []
        employee_count_list = []

        # Проходим по каждому месяцу и добавляем данные в соответствующий список
        for i, data in combined_data.items():
            values = data.split('|')
            net_profit_list.append(values[0])
            profitability_list.append(values[1])
            operating_expenses_list.append(values[2])
            customer_base_list.append(values[3])
            employee_count_list.append(values[4])

        # Объединяем списки в строки, разделенные запятыми
        forecast_data.net_profit = ','.join(net_profit_list)
        forecast_data.profitability = ','.join(profitability_list)
        forecast_data.operating_expenses = ','.join(operating_expenses_list)
        forecast_data.customer_base = ','.join(customer_base_list)
        forecast_data.employee_count = ','.join(employee_count_list)

        # Сохраняем объект модели
        forecast_data.save()

        monthly_search_koef = count_seasonal_coefficient(forecast_data.artefact, forecast_data.month)
        count_seasonality_indicator(monthly_search_koef, "all", forecast_data)

        forecast_for_net_profit = count_value_forecast(arr=forecast_data.get_net_profit(), alpha=forecast_data.seasonal_level,
                                  monthly_search_koef=monthly_search_koef)
        count_growth_stability_indicator(forecast_data.get_net_profit(), forecast_for_net_profit, "net_profit", forecast_data)
        count_coherence_indicator(forecast_data.get_net_profit(), forecast_data.seasonal_level, "net_profit", forecast_data)
        count_dynamics_indicator(forecast_data.get_net_profit(), forecast_data.seasonal_level, "net_profit", forecast_data)


        forecast_for_profitability = count_value_forecast(arr=forecast_data.get_profitability(), alpha=forecast_data.seasonal_level,
                                  monthly_search_koef=monthly_search_koef)
        count_growth_stability_indicator(forecast_data.get_profitability(), forecast_for_profitability, "profitability", forecast_data)
        count_coherence_indicator(forecast_data.get_profitability(), forecast_data.seasonal_level, "profitability", forecast_data)
        count_dynamics_indicator(forecast_data.get_profitability(), forecast_data.seasonal_level, "profitability", forecast_data)



        forecast_for_operating_expenses = count_value_forecast(arr=forecast_data.get_operating_expenses(), alpha=forecast_data.seasonal_level,
                                  monthly_search_koef=monthly_search_koef)
        count_growth_stability_indicator(forecast_data.get_operating_expenses(), forecast_for_operating_expenses, "operating_expenses", forecast_data)
        count_coherence_indicator(forecast_data.get_operating_expenses(), forecast_data.seasonal_level, "operating_expenses", forecast_data)
        count_dynamics_indicator(forecast_data.get_operating_expenses(), forecast_data.seasonal_level, "operating_expenses", forecast_data)



        forecast_for_customer_base = count_value_forecast(arr=forecast_data.get_customer_base(), alpha=forecast_data.seasonal_level,
                                  monthly_search_koef=monthly_search_koef)
        count_growth_stability_indicator(forecast_data.get_customer_base(), forecast_for_customer_base, "customer_base", forecast_data)
        count_coherence_indicator(forecast_data.get_customer_base(), forecast_data.seasonal_level, "customer_base", forecast_data)
        count_dynamics_indicator(forecast_data.get_customer_base(), forecast_data.seasonal_level, "customer_base", forecast_data)


        forecast_for_employee_count = count_value_forecast(arr=forecast_data.get_employee_count(), alpha=forecast_data.seasonal_level,
                                  monthly_search_koef=monthly_search_koef)
        count_growth_stability_indicator(forecast_data.get_employee_count(), forecast_for_employee_count, "employee_count", forecast_data)
        count_coherence_indicator(forecast_data.get_employee_count(), forecast_data.seasonal_level, "employee_count", forecast_data)
        count_dynamics_indicator(forecast_data.get_employee_count(), forecast_data.seasonal_level, "employee_count", forecast_data)

        # Получаем все индикаторы, связанные с этим объектом ForecastData
        seasonality_indicators = forecast_data.seasonality_indicators.all()
        growth_stability_indicators = forecast_data.growth_stability_indicators.all()
        coherence_indicators = forecast_data.coherence_indicators.all()
        dynamics_indicators = forecast_data.dynamics_indicators.all()

        # Создаем объект модели ForecastResult
        final_efficiency_result = (0.3 * ((seasonality_indicators[0].indicator_value+
                                        growth_stability_indicators[0].indicator_value+
                                        coherence_indicators[0].indicator_value+
                                        dynamics_indicators[0].indicator_value)/4)
                                   +0.25 * ((seasonality_indicators[0].indicator_value+
                                        growth_stability_indicators[1].indicator_value+
                                        coherence_indicators[1].indicator_value+
                                        dynamics_indicators[1].indicator_value)/4)
                                   +0.2 * ((seasonality_indicators[0].indicator_value+
                                        growth_stability_indicators[2].indicator_value+
                                        coherence_indicators[2].indicator_value+
                                        dynamics_indicators[2].indicator_value)/4)
                                   + 0.15 * ((seasonality_indicators[0].indicator_value +
                                             growth_stability_indicators[3].indicator_value +
                                             coherence_indicators[3].indicator_value +
                                             dynamics_indicators[3].indicator_value) / 4)
                                   + 0.1 * ((seasonality_indicators[0].indicator_value +
                                              growth_stability_indicators[4].indicator_value +
                                              coherence_indicators[4].indicator_value +
                                              dynamics_indicators[4].indicator_value) / 4)
                                   )
        result = ForecastResult.objects.create(
            forecast_data=forecast_data,
            success_probability=final_efficiency_result*100,
            result_comment='Сгенерирован на основе применения индикаторов',
            seasonal_koef=monthly_search_koef
        )

        return redirect('result_view', result_id=result.id)

    else:
        form = ForecastDataForm()

    results = ForecastResult.objects.all()

    return render(request, 'forecast/forecast_form.html',
                  {'form': form, 'period_month': period_month, 'results': results})

def result_view(request, result_id):
    result = ForecastResult.objects.get(id=result_id)
    forecast_data = result.forecast_data
    # Получение значений count()
    cc_net_profit = count_all_moving_averages(forecast_data.get_net_profit())
    ec_net_profit = count_all_exponential_smoothing(forecast_data.get_net_profit(), forecast_data.seasonal_level)

    cc_profitability = count_all_moving_averages(forecast_data.get_profitability())
    ec_profitability = count_all_exponential_smoothing(forecast_data.get_profitability(), forecast_data.seasonal_level)

    cc_operating_expenses = count_all_moving_averages(forecast_data.get_operating_expenses())
    ec_operating_expenses = count_all_exponential_smoothing(forecast_data.get_operating_expenses(),
                                                            forecast_data.seasonal_level)

    cc_customer_base = count_all_moving_averages(forecast_data.get_customer_base())
    ec_customer_base = count_all_exponential_smoothing(forecast_data.get_customer_base(), forecast_data.seasonal_level)

    cc_employee_count = count_all_moving_averages(forecast_data.get_employee_count())
    ec_employee_count = count_all_exponential_smoothing(forecast_data.get_employee_count(),
                                                        forecast_data.seasonal_level)

    #Получение значений индикаторов
    seasonality_indicators = forecast_data.seasonality_indicators.all()
    growth_stability_indicators = forecast_data.growth_stability_indicators.all()
    coherence_indicators = forecast_data.coherence_indicators.all()
    dynamics_indicators = forecast_data.dynamics_indicators.all()

    net_profit_indicators = []
    net_profit_indicators.append(seasonality_indicators[0].indicator_value)
    net_profit_indicators.append(growth_stability_indicators[0].indicator_value)
    net_profit_indicators.append(coherence_indicators[0].indicator_value)
    net_profit_indicators.append(dynamics_indicators[0].indicator_value)

    profitability_indicators = []
    profitability_indicators.append(seasonality_indicators[0].indicator_value)
    profitability_indicators.append(growth_stability_indicators[1].indicator_value)
    profitability_indicators.append(coherence_indicators[1].indicator_value)
    profitability_indicators.append(dynamics_indicators[1].indicator_value)

    operating_expenses_indicators = []
    operating_expenses_indicators.append(seasonality_indicators[0].indicator_value)
    operating_expenses_indicators.append(growth_stability_indicators[2].indicator_value)
    operating_expenses_indicators.append(coherence_indicators[2].indicator_value)
    operating_expenses_indicators.append(dynamics_indicators[2].indicator_value)

    customer_base_indicators = []
    customer_base_indicators.append(seasonality_indicators[0].indicator_value)
    customer_base_indicators.append(growth_stability_indicators[3].indicator_value)
    customer_base_indicators.append(coherence_indicators[3].indicator_value)
    customer_base_indicators.append(dynamics_indicators[3].indicator_value)

    employee_count_indicators = []
    employee_count_indicators.append(seasonality_indicators[0].indicator_value)
    employee_count_indicators.append(growth_stability_indicators[4].indicator_value)
    employee_count_indicators.append(coherence_indicators[4].indicator_value)
    employee_count_indicators.append(dynamics_indicators[4].indicator_value)

    return render(request, 'forecast/result.html', {
        'result': result,
        'forecast_data': forecast_data,
        'cc_net_profit': cc_net_profit,
        'ec_net_profit': ec_net_profit,
        'cc_profitability': cc_profitability,
        'ec_profitability': ec_profitability,
        'cc_operating_expenses': cc_operating_expenses,
        'ec_operating_expenses': ec_operating_expenses,
        'cc_customer_base': cc_customer_base,
        'ec_customer_base': ec_customer_base,
        'cc_employee_count': cc_employee_count,
        'ec_employee_count': ec_employee_count,
        'net_profit_indicators': net_profit_indicators,
        'profitability_indicators': profitability_indicators,
        'operating_expenses_indicators': operating_expenses_indicators,
        'customer_base_indicators': customer_base_indicators,
        'employee_count_indicators': employee_count_indicators,
    })

def count_value_forecast(arr, alpha, monthly_search_koef):

    result = 0

    averages = count_all_moving_averages(arr)
    final_average = sum(averages)/len(averages)
    print("Final average is " + str(final_average))

    all_smoothing = count_all_exponential_smoothing(arr, alpha)
    final_smoothing = all_smoothing[-1]
    print("Final smoothing is " + str(final_smoothing))

    print("Final seasonal koef is ")
    print(monthly_search_koef)

    result = monthly_search_koef*((final_average+final_smoothing)/2)

    return result

def count_all_moving_averages(arr):

    start = 0
    count = 0
    all_averages = []
    while (count < len(arr)-2):
        count += 1
        end = start+2

        average = sum(arr[start:end+1])/3
        all_averages.append(average)

        start += 1

    return all_averages

def count_all_exponential_smoothing(arr, alpha):

    all_smoothing = []
    all_smoothing.append(arr[0]) #Первое значение - первое наблюдение

    i = 1
    while i < len(arr):
        current_smoothing = alpha*arr[i] + ((1-alpha)*all_smoothing[-1])
        all_smoothing.append(current_smoothing)
        i += 1

    return all_smoothing

def count_seasonal_coefficient(artefact, month):
    def get_monthly_search_volume(keyword):
        pytrends = TrendReq(hl='en-US', tz=360)

        # Определение временного интервала за прошлый год
        current_date = datetime.date.today()
        start_date = datetime.date(current_date.year - 1, 1, 1)

        monthly_data = []

        # Получение данных о количестве поисковых запросов для каждого месяца прошлого года
        for month in range(1, 13):
            start_of_month = datetime.date(start_date.year, month, 1)
            end_of_month = datetime.date(start_date.year, month, calendar.monthrange(start_date.year, month)[1])

            timeframe = f'{start_of_month.strftime("%Y-%m-%d")} {end_of_month.strftime("%Y-%m-%d")}'
            pytrends.build_payload(kw_list=[keyword],
                                   timeframe=timeframe)  # Используем параметр geo по умолчанию (мировой)
            interest_data = pytrends.interest_over_time()
            #time.sleep(10)  # Добавлено для предотвращения слишком частых запросов к API
            # Преобразование результата в int
            if not interest_data.empty:
                monthly_data.append(int(interest_data[keyword].sum()))
            else:
                monthly_data.append(0)
        return monthly_data

    def get_month_number(month_name):
        # Словарь сопоставления названий месяцев и номеров
        months = {
            'январь': 1,
            'февраль': 2,
            'март': 3,
            'апрель': 4,
            'май': 5,
            'июнь': 6,
            'июль': 7,
            'август': 8,
            'сентябрь': 9,
            'октябрь': 10,
            'ноябрь': 11,
            'декабрь': 12
        }

        # Приведение введенного названия месяца к нижнему регистру для корректного сравнения
        month_name = month_name.lower()

        # Возврат номера месяца или None, если такого месяца нет
        return months.get(month_name, None)

    keyword = artefact
    monthly_search_volume = get_monthly_search_volume(keyword)
    average = sum(monthly_search_volume)/len(monthly_search_volume)

    i = 0
    while i < len(monthly_search_volume):
        monthly_search_volume[i]=monthly_search_volume[i]/average
        i+=1

    print("Seasonal koefs are ")
    print(monthly_search_volume)

    return monthly_search_volume[get_month_number(month)-1]

def count_seasonality_indicator(monthly_search_koef, param, data):
    if (monthly_search_koef >= 0.99):
        SeasonalityIndicator.objects.create(indicator_value=1, param=param, forecast_data=data)
    else:
        SeasonalityIndicator.objects.create(indicator_value=0, param=param, forecast_data=data)

def count_growth_stability_indicator(arr, final_forecast, param, data):
    final_average = sum(count_all_moving_averages(arr)) / len(count_all_moving_averages(arr))
    total_growth = 0
    for i in range(1, len(arr)):
        difference = arr[i] - arr[i - 1]
        total_growth += difference
    G = 0.05
    if ((final_average*(1+G) <= final_forecast) or (total_growth>0)):
        GrowthStabilityIndicator.objects.create(indicator_value=1, param=param, forecast_data=data)
    else:
        GrowthStabilityIndicator.objects.create(indicator_value=0, param=param, forecast_data=data)

def count_coherence_indicator(arr, alpha, param, data):
    final_smoothing = count_all_exponential_smoothing(arr, alpha)[-1]
    final_average = sum(count_all_moving_averages(arr)) / len(count_all_moving_averages(arr))

    if (1-(abs(final_average - final_smoothing)/final_average)>= 0.85):
        CoherenceIndicator.objects.create(indicator_value=1, param=param, forecast_data=data)
    else:
        CoherenceIndicator.objects.create(indicator_value=0, param=param, forecast_data=data)

def count_dynamics_indicator(arr, alpha, param, data):

    all_values = count_all_exponential_smoothing(arr, alpha)
    total_difference = 0

    # Вычисление разниц между последовательными элементами
    for i in range(1, len(all_values)):
        difference = all_values[i] - all_values[i - 1]
        total_difference += difference

    if (total_difference >= 0):
        DynamicsIndicator.objects.create(indicator_value=1, param=param, forecast_data=data)
    else:
        DynamicsIndicator.objects.create(indicator_value=0, param=param, forecast_data=data)