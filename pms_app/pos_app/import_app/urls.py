from django.conf.urls import patterns, url
from pms_app.pos_app.import_app import views

urlpatterns = patterns(
    'pms_app.pos_app.import_app',
    # index: select csv files page
    url(r'^index/$', views.index, name='pos_import_app_index'),

    # complete: open csv file and insert data to db
    url(r'^complete/$', views.complete, name='pos_import_app_complete'),
    url(r'^complete/(?P<date>[-\w]+)/$', views.complete, name='pos_import_app_complete'),

    # javascript: webix.js, logic.js
    url(r'^webix.js', views.webix_js, name='pos_import_webix_js'),
    url(r'^logic.js', views.logic_js, name='pos_import_logic_js'),

    # json: pos_files.json
    url(r'^files.json', views.files_json, name='pos_import_files_json')
)
