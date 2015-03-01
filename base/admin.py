# noinspection PyUnresolvedReferences
from django.contrib import admin
from base.views import *


admin.site.register_view(
    'base/model_list/$',
    urlname='base_model_list',
    view=base_model_list
)