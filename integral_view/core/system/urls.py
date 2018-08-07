from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from integral_view.core.system.views.ntp_management import update_ntp_settings, view_ntp_settings, sync_ntp
from integral_view.core.system.views.services_management import view_services, update_service_status
from integral_view.core.system.views.system_management import update_system_date_time, reset_to_factory_defaults, download_sys_info, upload_sys_info, view_system_info, update_manifest, update_org_info, view_email_settings, update_email_settings, view_https_mode, update_https_mode, reboot_or_shutdown, access_shell, flag_node
from integral_view.core.system.views.scheduled_notification_management import view_scheduled_notifications, create_scheduled_notification, delete_scheduled_notification
from integral_view.core.system.views.log_management import download_log, view_audits, view_hardware_logs


urlpatterns = patterns('',
                       url(r'^$', login_required(view_system_info)),

                       # From views/log_management.py
                       url(r'^view_audits/', login_required(view_audits)),
                       url(r'^view_hardware_logs/',
                           login_required(view_hardware_logs)),
                       url(r'^download_log/', login_required(download_log)),

                       # Form views/system_management.py
                       url(r'^update_system_date_time/',
                           login_required(update_system_date_time)),
                       url(r'^reset_to_factory_defaults/',
                           login_required(reset_to_factory_defaults)),
                       url(r'^update_org_info/',
                           login_required(update_org_info)),
                       url(r'^download_sys_info/',
                           login_required(download_sys_info)),
                       url(r'^upload_sys_info/', login_required(upload_sys_info)),
                       url(r'^view_system_info/',
                           login_required(view_system_info)),
                       url(r'^update_manifest/', login_required(update_manifest)),
                       url(r'^flag_node/', flag_node),
                       url(r'^access_shell/', login_required(access_shell)),
                       url(r'^view_email_settings/',
                           login_required(view_email_settings)),
                       url(r'^update_email_settings/',
                           login_required(update_email_settings)),
                       url(r'^view_https_mode/', login_required(view_https_mode)),
                       url(r'^update_https_mode/',
                           login_required(update_https_mode)),
                       url(r'^reboot_or_shutdown',
                           login_required(reboot_or_shutdown)),

                       # From views/ntp_management.py
                       url(r'^view_ntp_settings/',
                           login_required(view_ntp_settings)),
                       url(r'^update_ntp_settings/',
                           login_required(update_ntp_settings)),
                       url(r'^sync_ntp/',
                           login_required(sync_ntp)),


                       # From views/services_management.py
                       url(r'^view_services/', login_required(view_services)),
                       url(r'^update_service_status/',
                           login_required(update_service_status)),


                       # From views/scheduled_notification_management.py
                       url(r'^view_scheduled_notifications/',
                           view_scheduled_notifications),
                       url(r'^create_scheduled_notification/',
                           create_scheduled_notification),
                       url(r'^delete_scheduled_notification/',
                           delete_scheduled_notification),

                        )
# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
