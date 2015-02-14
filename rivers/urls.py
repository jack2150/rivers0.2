from django.conf.urls import patterns, include, url
from django.contrib import admin
from adminplus.sites import AdminSitePlus

admin.site = AdminSitePlus()
admin.autodiscover()
admin.site.login_template = 'admin/login.html'

urlpatterns = patterns(
    '',

    # admin
    url(r'^admin/', include(admin.site.urls)),

)
