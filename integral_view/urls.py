from django.conf.urls import patterns, include, url

from django.contrib.auth.decorators import login_required

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from integral_view.views.admin_auth import login, logout, update_admin_password

from integralstor import config
applications, err = config.get_applications_config()
app_patterns = []
if applications:
    for app_tag in applications.keys():
        try:
            app_patterns.append(url(r'^applications/%s/'%app_tag, include('integral_view.applications.%s.urls'%app_tag)))
        except Exception, e:
            pass

urlpatterns = [
                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', admin.site.urls),

                       url(r'^storage/', include('integral_view.core.storage.urls')),
                       url(r'^replication/', include('integral_view.core.replication.urls')),
                       url(r'^application_management/', include('integral_view.core.application_management.urls')),
                       url(r'^tasks/', include('integral_view.core.tasks.urls')),
                       url(r'^monitoring/', include('integral_view.core.monitoring.urls')),
                       url(r'^networking/', include('integral_view.core.networking.urls')),
                       url(r'^users_groups/', include('integral_view.core.users_groups.urls')),
                       url(r'^keys_certs/', include('integral_view.core.keys_certs.urls')),
                       url(r'^storage_access/', include('integral_view.core.storage_access.urls')),
                       url(r'^system/', include('integral_view.core.system.urls')),

                       # From views/admin_auth.py
                       url(r'^login/', login),
                       url(r'^logout/', logout, name="logout"),
                       url(r'^$', login),
                       url(r'^update_admin_password/',
                           login_required(update_admin_password))
]

if app_patterns:
    urlpatterns.extend(app_patterns)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
