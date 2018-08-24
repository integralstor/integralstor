from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from integral_view.core.networking.views.networking_management import view_interfaces, view_interface, view_bond, update_interface_state, update_interface_address, delete_interface_connection, create_bond, delete_bond, view_hostname, update_hostname, view_dns_nameservers, update_dns_nameservers, delete_vlan, create_vlan

urlpatterns = [
                       url(r'^$', login_required(view_interfaces)),

                       # From views/networking_management.py
                       url(r'^view_interfaces/', login_required(view_interfaces)),
                       url(r'^view_interface/', login_required(view_interface)),
                       url(r'^update_interface_state/',
                           login_required(update_interface_state)),
                       url(r'^view_bond/', login_required(view_bond)),
                       url(r'^update_interface_address/',
                           login_required(update_interface_address)),
                       url(r'^delete_interface_connection/',
                           login_required(delete_interface_connection)),
                       url(r'^create_vlan/', login_required(create_vlan)),
                       url(r'^delete_vlan/', login_required(delete_vlan)),
                       url(r'^create_bond/', login_required(create_bond)),
                       url(r'^delete_bond/', login_required(delete_bond)),
                       url(r'^view_hostname/', login_required(view_hostname)),
                       url(r'^update_hostname/', login_required(update_hostname)),
                       url(r'^view_dns_nameservers/',
                           login_required(view_dns_nameservers)),
                       url(r'^update_dns_nameservers/',
                           login_required(update_dns_nameservers)),
]
# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
