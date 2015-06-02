from django.conf.urls import patterns, include, url
from integral_view.views.admin_auth  import login, logout, change_admin_password, configure_email_settings 
from integral_view.views.common import show, refresh_alerts, raise_alert, internal_audit, configure_ntp_settings, reset_to_factory_defaults, flag_node
from integral_view.views.log_management import  download_sys_log, rotate_log, view_rotated_log_list, view_rotated_log_file, edit_integral_view_log_level
from integral_view.views.share_management import display_shares, create_share, samba_server_settings, save_samba_server_settings, view_share, edit_share, delete_share, edit_auth_method, view_local_users, create_local_user, change_local_user_password, delete_local_user
from integral_view.views.nfs_share_management import view_nfs_shares, view_nfs_share, delete_nfs_share
from integral_view.views.zfs_management import view_zfs_pools, view_zfs_pool
from django.contrib.auth.decorators import login_required
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'integral_view.views.home', name='home'),
    # url(r'^integral_view/', include('integral_view.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', login),
    url(r'^$', login),
    url(r'^raise_alert/', raise_alert),
    url(r'^flag_node/', flag_node),
    url(r'^internal_audit/', internal_audit),
    url(r'^change_admin_password/', login_required(change_admin_password),name="change_admin_password"),
    url(r'^configure_email_settings/', login_required(configure_email_settings)),
    url(r'^reset_to_factory_defaults/', login_required(reset_to_factory_defaults)),
    url(r'^configure_ntp_settings/', login_required(configure_ntp_settings)),
    url(r'^display_shares/', login_required(display_shares)),
    url(r'^view_local_users/', login_required(view_local_users)),
    url(r'^create_local_user/', login_required(create_local_user)),
    url(r'^delete_local_user/', login_required(delete_local_user)),
    url(r'^change_local_user_password/', login_required(change_local_user_password)),
    url(r'^view_zfs_pools/', login_required(view_zfs_pools)),
    url(r'^view_zfs_pool/', login_required(view_zfs_pool)),
    url(r'^view_nfs_shares/', login_required(view_nfs_shares)),
    url(r'^view_nfs_share/', login_required(view_nfs_share)),
    url(r'^delete_nfs_share/', login_required(delete_nfs_share)),
    url(r'^create_share/', login_required(create_share)),
    url(r'^view_share/', login_required(view_share)),
    url(r'^edit_share/', login_required(edit_share)),
    url(r'^edit_auth_method/', login_required(edit_auth_method)),
    url(r'^delete_share/', login_required(delete_share)),
    url(r'^auth_server_settings/', login_required(samba_server_settings)),
    url(r'^save_samba_server_settings/', login_required(save_samba_server_settings)),
    #url(r'^replace_disk/', login_required(replace_disk)),
    url(r'^edit_integral_view_log_level/', login_required(edit_integral_view_log_level)),
    url(r'^show/([A-Za-z0-9_]+)/([a-zA-Z0-9_\-\.]*)', login_required(show),name="show_page"),
    url(r'^refresh_alerts/([0-9_]*)', login_required(refresh_alerts)),
    url(r'^logout/', logout,name="logout"),
    url(r'^download_sys_log/', login_required(download_sys_log)),
    url(r'^rotate_log/([A-Za-z_]+)', login_required(rotate_log)),
    url(r'^view_rotated_log_list/([A-Za-z_]+)', login_required(view_rotated_log_list)),
    url(r'^view_rotated_log_file/([A-Za-z_]+)', login_required(view_rotated_log_file)),
)

