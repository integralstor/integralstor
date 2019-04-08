from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from views.urbackup import view_backup


urlpatterns = patterns('',
                       url(r'^$', login_required(view_backup)),

                       # From views/urbackup.py
                       url(r'^view_backup/',
                           login_required(view_backup)),
                        )
# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
