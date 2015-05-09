# noinspection PyUnresolvedReferences
from django.contrib import admin
from base.views import *


admin.site.register_view(
    'base/model_list/$',
    urlname='base_models_view',
    view=base_models_view
)