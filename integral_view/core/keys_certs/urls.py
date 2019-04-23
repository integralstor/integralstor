from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from integral_view.core.keys_certs.views.keys_certs_management import view_ssl_certificates, delete_ssl_certificate, create_self_signed_ssl_certificate, upload_ssl_certificate, view_known_hosts_ssh_keys, view_user_ssh_keys, upload_ssh_user_key, upload_ssh_host_key

urlpatterns = [
                       url(r'^$', login_required(view_user_ssh_keys)),

                       # From views/keys_certs_management.py
                       url(r'^view_ssl_certificates/',
                           login_required(view_ssl_certificates)),
                       url(r'^delete_ssl_certificate/',
                           login_required(delete_ssl_certificate)),
                       url(r'^create_self_signed_ssl_certificate/',
                           login_required(create_self_signed_ssl_certificate)),
                       url(r'^upload_ssl_certificate/',
                           login_required(upload_ssl_certificate)),
                       url(r'^upload_ssh_user_key',
                           login_required(upload_ssh_user_key)),
                       url(r'^upload_ssh_host_key',
                           login_required(upload_ssh_host_key)),
                       url(r'^view_user_ssh_keys',
                           login_required(view_user_ssh_keys)),
                       url(r'^view_known_hosts_ssh_keys',
                           login_required(view_known_hosts_ssh_keys))
]
# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
