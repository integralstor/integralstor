from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from integral_view.core.replication.views.remote_replication_management import create_remote_replication, view_remote_replications, delete_remote_replication, update_remote_replication, update_rsync_remote_replication_pause_schedule, update_remote_replication_user_comment

urlpatterns = [
                       url(r'^$', login_required(view_remote_replications)),

                       # From views/remote_replication_management.py
                       url(r'^view_remote_replications/',
                           login_required(view_remote_replications)),
                       url(r'^create_remote_replication/',
                           login_required(create_remote_replication)),
                       url(r'^update_remote_replication_user_comment/',
                           login_required(update_remote_replication_user_comment)),
                       url(r'^update_remote_replication/',
                           login_required(update_remote_replication)),
                       url(r'^update_rsync_remote_replication_pause_schedule/',
                           login_required(update_rsync_remote_replication_pause_schedule)),
                       url(r'^delete_remote_replication/',
                           login_required(delete_remote_replication)),
]
# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
