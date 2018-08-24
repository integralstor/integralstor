from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from integral_view.applications.storage_insights.views.scan_management import view_scans, delete_scan, view_scan_configurations, create_scan_configuration, delete_scan_configuration, update_scan_schedule, delete_scan_schedule
from integral_view.applications.storage_insights.views.query_management import view_dashboard, view_query_types, view_files_by_extension, view_general_query_results, find_files, download_file

urlpatterns = [
                       url(r'^view_dashboard/', login_required(view_dashboard)),
                       url(r'^view_general_query_results/', login_required(view_general_query_results)),
                       url(r'^view_files_by_extension/', login_required(view_files_by_extension)),
                       url(r'^view_query_types/', login_required(view_query_types)),
                       url(r'^find_files/', login_required(find_files)),
                       url(r'^download_file/', login_required(download_file)),
                       url(r'^view_scans/', login_required(view_scans)),
                       url(r'^delete_scan/', login_required(delete_scan)),
                       url(r'^update_scan_schedule/', login_required(update_scan_schedule)),
                       url(r'^delete_scan_schedule/', login_required(delete_scan_schedule)),
                       url(r'^view_scan_configurations/', login_required(view_scan_configurations)),
                       url(r'^create_scan_configuration/', login_required(create_scan_configuration)),
                       url(r'^delete_scan_configuration/', login_required(delete_scan_configuration)),

                       url(r'^$', login_required(view_dashboard)),
]
# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
