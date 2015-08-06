from django.conf.urls import patterns, include, url
from integral_view.views.admin_auth  import login, logout, change_admin_password, configure_email_settings 
from integral_view.views.common import show, refresh_alerts, raise_alert, internal_audit, configure_ntp_settings, reset_to_factory_defaults, flag_node, set_file_owner_and_permissions,dir_contents
from integral_view.views.log_management import  download_sys_log, rotate_log, view_rotated_log_list, view_rotated_log_file, edit_integral_view_log_level
from integral_view.views.cifs_share_management import view_cifs_shares, create_cifs_share, samba_server_settings, save_samba_server_settings, view_cifs_share, edit_cifs_share, delete_cifs_share, edit_auth_method
from integral_view.views.local_user_management import view_local_users, create_local_user, change_local_user_password, delete_local_user, view_local_user, edit_local_user_gid, view_local_groups, edit_local_user_group_membership, view_local_group, create_local_group, delete_local_group
from integral_view.views.nfs_share_management import view_nfs_shares, view_nfs_share, delete_nfs_share, create_nfs_share
from integral_view.views.zfs_management import view_zfs_pools, view_zfs_pool, view_zfs_dataset, edit_zfs_dataset, delete_zfs_dataset, create_zfs_dataset, view_zfs_snapshots, create_zfs_snapshot, delete_zfs_snapshot, rename_zfs_snapshot, rollback_zfs_snapshot, create_zfs_pool, delete_zfs_pool, set_zfs_slog, remove_zfs_slog, scrub_zfs_pool, create_zfs_zvol, view_zfs_zvol
#from zfs.zfs_management import view_zfs_pools, view_zfs_pool, view_zfs_dataset, edit_zfs_dataset, delete_zfs_dataset, create_zfs_dataset, view_zfs_snapshots, create_zfs_snapshot, delete_zfs_snapshot, rename_zfs_snapshot, rollback_zfs_snapshot, create_zfs_pool, delete_zfs_pool, set_zfs_slog
from integral_view.views.networking_management import view_interfaces, view_nic, view_bond, set_interface_state, edit_interface_address, create_bond, remove_bond, view_hostname, edit_hostname, view_dns_nameservers, edit_dns_nameservers
from integral_view.views.services_management import view_services, change_service_status
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
    url(r'^set_file_owner_and_permissions/', set_file_owner_and_permissions),
    url(r'^internal_audit/', internal_audit),
    url(r'^change_admin_password/', login_required(change_admin_password),name="change_admin_password"),
    url(r'^configure_email_settings/', login_required(configure_email_settings)),
    url(r'^reset_to_factory_defaults/', login_required(reset_to_factory_defaults)),
    url(r'^configure_ntp_settings/', login_required(configure_ntp_settings)),
    url(r'^view_cifs_shares/', login_required(view_cifs_shares)),
    url(r'^view_services/', login_required(view_services)),
    url(r'^change_service_status/', login_required(change_service_status)),
    url(r'^view_interfaces/', login_required(view_interfaces)),
    url(r'^set_interface_state/', login_required(set_interface_state)),
    url(r'^edit_interface_address/', login_required(edit_interface_address)),
    url(r'^view_nic/', login_required(view_nic)),
    url(r'^view_hostname/', login_required(view_hostname)),
    url(r'^edit_hostname/', login_required(edit_hostname)),
    url(r'^view_dns_nameservers/', login_required(view_dns_nameservers)),
    url(r'^edit_dns_nameservers/', login_required(edit_dns_nameservers)),
    url(r'^view_bond/', login_required(view_bond)),
    url(r'^remove_bond/', login_required(remove_bond)),
    url(r'^create_bond/', login_required(create_bond)),
    url(r'^edit_local_user_gid/', login_required(edit_local_user_gid)),
    url(r'^edit_local_user_group_membership/', login_required(edit_local_user_group_membership)),
    url(r'^view_local_user/', login_required(view_local_user)),
    url(r'^view_local_users/', login_required(view_local_users)),
    url(r'^create_local_group/', login_required(create_local_group)),
    url(r'^delete_local_group/', login_required(delete_local_group)),
    url(r'^view_local_group/', login_required(view_local_group)),
    url(r'^view_local_groups/', login_required(view_local_groups)),
    url(r'^create_local_user/', login_required(create_local_user)),
    url(r'^delete_local_user/', login_required(delete_local_user)),
    url(r'^change_local_user_password/', login_required(change_local_user_password)),
    url(r'^view_zfs_snapshots/', login_required(view_zfs_snapshots)),
    url(r'^create_zfs_snapshot/', login_required(create_zfs_snapshot)),
    url(r'^rename_zfs_snapshot/', login_required(rename_zfs_snapshot)),
    url(r'^delete_zfs_snapshot/', login_required(delete_zfs_snapshot)),
    url(r'^rollback_zfs_snapshot/', login_required(rollback_zfs_snapshot)),
    url(r'^view_zfs_pools/', login_required(view_zfs_pools)),
    url(r'^set_zfs_slog/', login_required(set_zfs_slog)),
    url(r'^remove_zfs_slog/', login_required(remove_zfs_slog)),
    url(r'^view_zfs_pool/', login_required(view_zfs_pool)),
    url(r'^create_zfs_pool/', login_required(create_zfs_pool)),
    url(r'^delete_zfs_pool/', login_required(delete_zfs_pool)),
    url(r'^scrub_zfs_pool/', login_required(scrub_zfs_pool)),
    url(r'^view_zfs_dataset/', login_required(view_zfs_dataset)),
    url(r'^edit_zfs_dataset/', login_required(edit_zfs_dataset)),
    url(r'^delete_zfs_dataset/', login_required(delete_zfs_dataset)),
    url(r'^create_zfs_dataset/', login_required(create_zfs_dataset)),
    url(r'^create_zfs_zvol/', login_required(create_zfs_zvol)),
    url(r'^view_zfs_zvol/', login_required(view_zfs_zvol)),
    url(r'^create_nfs_share/', login_required(create_nfs_share)),
    url(r'^view_nfs_shares/', login_required(view_nfs_shares)),
    url(r'^view_nfs_share/', login_required(view_nfs_share)),
    url(r'^delete_nfs_share/', login_required(delete_nfs_share)),
    url(r'^create_cifs_share/', login_required(create_cifs_share)),
    url(r'^view_cifs_share/', login_required(view_cifs_share)),
    url(r'^view_cifs_shares/', login_required(view_cifs_shares)),
    url(r'^edit_cifs_share/', login_required(edit_cifs_share)),
    url(r'^edit_auth_method/', login_required(edit_auth_method)),
    url(r'^delete_cifs_share/', login_required(delete_cifs_share)),
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
    url(r'dir_contents/',login_required(dir_contents)),
)

