from django.conf.urls import patterns, include, url
from django.contrib import admin

#from pms_app.admin import admin_site
#from pms_app.pos_app import views

admin.autodiscover()

urlpatterns = patterns(
    '',
    # base_app
    url(r'^base/', include('base_app.urls')),

    # admin
    #url(r'^admin/pos_app/import_pos_csv', views.admin_import_pos_csv, name='admin_import_pos_csv'),
    #url(r'^admin_site/', include(admin_site.urls)),
    url(r'^admin/', include(admin.site.urls)),

)
