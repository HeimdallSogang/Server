from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Currency)

admin.site.register(Stock)

admin.site.register(Report)

admin.site.register(Analyst)

admin.site.register(Point)

admin.site.register(Writes)