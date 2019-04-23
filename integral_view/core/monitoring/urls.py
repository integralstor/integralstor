from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from integral_view.core.monitoring.views.monitoring import view_read_write_stats, api_get_status, view_remote_monitoring_servers, update_remote_monitoring_server, delete_remote_monitoring_server, view_remote_monitoring_server_status, refresh_alerts, view_alerts, view_dashboard

urlpatterns = [
                       url(r'^$', login_required(view_dashboard)),

                       # From views/monitoring.py
                       url(r'^view_dashboard/([A-Za-z0-9_]*)',
                           login_required(view_dashboard)),
                       url(r'^api_get_status/', api_get_status),
                       url(r'^view_remote_monitoring_servers/',
                           view_remote_monitoring_servers),
                       url(r'^update_remote_monitoring_server/',
                           update_remote_monitoring_server),
                       url(r'^delete_remote_monitoring_server/',
                           delete_remote_monitoring_server),
                       url(r'^view_remote_monitoring_server_status/',
                           view_remote_monitoring_server_status),

                       # From views/alerts_management.py
                       url(r'^view_alerts/', login_required(view_alerts)),
                       url(r'^refresh_alerts/([0-9_]*)',
                           login_required(refresh_alerts))
]
# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
