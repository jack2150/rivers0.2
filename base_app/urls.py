from django.conf.urls import patterns, url
from base_app import views

urlpatterns = patterns(
    'base_app',
    # index: currently testing only
    url(r'^index', views.index, name='base_index'),

    # javascript: webix.js
    url(r'^webix.js', views.webix_js, name='base_webix_js'),
    url(r'^logic.js', views.logic_js, name='base_logic_js'),
)
