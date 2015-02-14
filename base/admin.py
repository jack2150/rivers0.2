from django.contrib import admin
from base.views import base_models


# Register your models here.
admin.site.register_view(
    'base/models/$',
    urlname='base_models',
    view=base_models
)