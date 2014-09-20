from django.conf.urls import patterns, url
from pms_app.pos_app.view_app import views


urlpatterns = patterns(
    'pms_app.pos_app.view_app',
    # page: index
    url(r'^index/$', views.index, name='pos_view_app_index'),
    url(r'^index/(?P<date>[-\w]+)/$', views.index, name='pos_view_app_index'),

    # ajax: date exist
    url(r'^exists/$', views.date_exists, name='pos_view_date_exist'),
    url(r'^exists/(?P<date>[-\w]+)/$', views.date_exists, name='pos_view_date_exist'),

    # javascript: webix.js, logic.js
    url(r'^webix.js', views.webix_js, name='pos_view_webix_js'),
    url(r'^logic.js', views.logic_js, name='pos_view_logic_js'),

    # json: overall.json, positions.json
    url(r'^(?P<date>[-\w]+)/overall.json', views.overall_json, name='pos_view_overall_json'),
    url(r'^(?P<date>[-\w]+)/positions.json', views.positions_json, name='pos_view_positions_json'),

)
