from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    'pms_app.pos_app',
    url(r'^import/', include('pms_app.pos_app.import_app.urls')),
    url(r'^view/', include('pms_app.pos_app.view_app.urls')),


)
