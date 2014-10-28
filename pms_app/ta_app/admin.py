from django.contrib import admin
from pms_app.ta_app import models

admin.site.register(models.WorkingOrder)
admin.site.register(models.FilledOrder)
admin.site.register(models.CancelledOrder)
admin.site.register(models.RollingStrategy)
