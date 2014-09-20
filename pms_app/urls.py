from django.conf.urls import patterns, include, url
from pms_app import views


urlpatterns = patterns(
    'pms_app',
    url(r'^pos/', include('pms_app.pos_app.urls')),
    url(r'^spread/', include('pms_app.spr_app.urls')),

    url(r'links.js', views.links, name='pms_app_links'),
)
