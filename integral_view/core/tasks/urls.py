from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from integral_view.core.tasks.views.task_management import view_background_tasks, view_task_details, delete_background_task, stop_background_task, view_scheduled_tasks, update_scheduled_task_schedule


urlpatterns = patterns('',
                       url(r'^$', login_required(view_scheduled_tasks)),

                       # From views/task_management.py
                       url(r'^view_background_tasks/',
                           login_required(view_background_tasks)),
                       url(r'^delete_background_task/',
                           login_required(delete_background_task)),
                       url(r'^stop_background_task/',
                           login_required(stop_background_task)),
                       url(r'^view_task_details/([0-9]*)',
                           login_required(view_task_details)),
                       url(r'^view_scheduled_tasks/',
                           login_required(view_scheduled_tasks)),
                       url(r'^update_scheduled_task_schedule/',
                           login_required(update_scheduled_task_schedule)),
                        )
# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
