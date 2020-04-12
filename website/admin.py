from django.contrib import admin

# Register your models here.

from .models import Fruit, QueryResult

admin.site.register(Fruit)
admin.site.register(QueryResult)