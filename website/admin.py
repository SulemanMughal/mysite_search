from django.contrib import admin

# Register your models here.

from .models import Fruit, QueryResult, ColorRange, configurationRules, configResultsDataBase

admin.site.register(Fruit)
# admin.site.register(QueryResult)
admin.site.register(ColorRange)
admin.site.register(configurationRules)
admin.site.register(configResultsDataBase)