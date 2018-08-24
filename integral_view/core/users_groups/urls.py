from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from integral_view.core.users_groups.views.local_user_management import view_local_users, create_local_user, update_local_user_password, delete_local_user, view_local_user, view_local_groups, update_local_user_group_membership, view_local_group, create_local_group, delete_local_group, update_group_membership

urlpatterns = [
                       url(r'^$', login_required(view_local_users)),

                       # From views/local_user_management.py
                       url(r'^view_local_users/',
                           login_required(view_local_users)),
                       url(r'^view_local_groups/',
                           login_required(view_local_groups)),
                       url(r'^view_local_user/', login_required(view_local_user)),
                       url(r'^view_local_group/',
                           login_required(view_local_group)),
                       url(r'^update_local_user_group_membership/',
                           login_required(update_local_user_group_membership)),
                       url(r'^create_local_user/',
                           login_required(create_local_user)),
                       url(r'^delete_local_group/',
                           login_required(delete_local_group)),
                       url(r'^create_local_group/',
                           login_required(create_local_group)),
                       url(r'^delete_local_user/',
                           login_required(delete_local_user)),
                       url(r'^update_local_user_password/',
                           login_required(update_local_user_password)),
                       url(r'^update_group_membership/',
                           login_required(update_group_membership)),
]

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
