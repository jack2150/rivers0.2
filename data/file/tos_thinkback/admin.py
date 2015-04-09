from django.contrib import admin
from data.file.tos_thinkback.views import *


admin.site.register_view(
    'tos_thinkback/import/select/$',
    urlname='tos_thinkback_import_select_view',
    view=tos_thinkback_import_select_view
)

admin.site.register_view(
    'tos_thinkback/import/run/$',
    urlname='tos_thinkback_import_run_view',
    view=tos_thinkback_import_run_view
)
admin.site.register_view(
    'tos_thinkback/import/run/(?P<symbol>\w+)/$',
    urlname='tos_thinkback_import_run_view',
    view=tos_thinkback_import_run_view
)