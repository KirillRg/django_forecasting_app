from django.contrib import admin

from .models import ForecastData, SeasonalityIndicator, GrowthStabilityIndicator, DynamicsIndicator, CoherenceIndicator, ForecastResult

admin.site.register(ForecastData)
admin.site.register(SeasonalityIndicator)
admin.site.register(GrowthStabilityIndicator)
admin.site.register(DynamicsIndicator)
admin.site.register(CoherenceIndicator)
admin.site.register(ForecastResult)
