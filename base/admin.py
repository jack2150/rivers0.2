from django.contrib import admin
from base.views import *


admin.site.register_view(
    'base/model_list/$',
    urlname='list_all_model_view',
    view=list_all_model
)