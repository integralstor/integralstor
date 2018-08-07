from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from integral_view.core.application_management.views.application_management import view_applications, launch_application


urlpatterns = patterns('',
                       url(r'^$', login_required(view_applications)),

                       # From views/application_management.py
                       url(r'^view_applications/',
                           login_required(view_applications)),
                       url(r'^launch_application/',
                           login_required(launch_application)),
                        )
# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
