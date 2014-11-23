from django.conf.urls import patterns, include, url
from django.contrib import admin

#from pms_app.admin import admin_site
#from pms_app.pos_app import views
from adminplus.sites import AdminSitePlus

admin.site = AdminSitePlus()
admin.autodiscover()

urlpatterns = patterns(
    '',

    # admin
    url(r'^admin/', include(admin.site.urls)),

)
