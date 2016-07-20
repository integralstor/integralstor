import django.template, django
from django.conf import settings
from django.contrib.auth.decorators import login_required
import django.http 

import os, os.path
from integralstor_common import scheduler_utils, common, command, zfs

def list_scheduled_jobs(request):
  return_dict = {}
  try:
    cron_jobs,err = scheduler_utils.list_all_cron()
    if err:
      raise Exception(err)
    snapshot_schedules, err = zfs.get_all_snapshot_schedules()
    if err:
      raise Exception(err)
    return_dict["snapshot_schedules"] = snapshot_schedules
    return_dict["cron_list"] = cron_jobs
    return django.shortcuts.render_to_response("view_cron_jobs.html", return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "scheduler_base.html"
    return_dict["page_title"] = 'Scheduled jobs'
    return_dict['tab'] = 'view_cron_jobs_tab'
    return_dict["error"] = 'Error loading scheduled jobs information'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def download_cron_log(request):
  response = django.http.HttpResponse()
  cron_name = request.POST.get('cron_name')
  try:
    response['Content-disposition'] = 'attachment; filename='+cron_name.replace(" ","_")+'.log'
    response['Content-type'] = 'application/x-compressed'
    with open(common.get_log_folder_path()+"/"+cron_name.replace(" ","_")+".log", 'rb') as f:
      byte = f.read(1)
      while byte:
        response.write(byte)
        byte = f.read(1)
        response.flush()
  except Exception as e:
    return django.http.HttpResponse(e)
  return response

def remove_cron_job(request):
  try:
    cron_name = request.POST.get('cron_name')
    delete,err = scheduler_utils.delete_cron_with_comment(cron_name)
    if err:
      raise Exception(err)
    if delete:
      return django.http.HttpResponseRedirect("/list_cron_jobs")
    else:
      raise Exception('Error deleting a scheduled job')
  except Exception, e:
    return_dict['base_template'] = "scheduler_base.html"
    return_dict["page_title"] = 'Scheduled jobs'
    return_dict['tab'] = 'view_cron_jobs_tab'
    return_dict["error"] = 'Error removing scheduled jobs information'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_background_tasks(request):
  return_dict = {}
  db_path = settings.DATABASES["default"]["NAME"]
  try:
    return_dict["back_jobs"] = scheduler_utils.get_background_jobs(db_path)[0]
    return django.shortcuts.render_to_response("view_background_tasks.html", return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "scheduler_base.html"
    return_dict["page_title"] = 'Background jobs'
    return_dict['tab'] = 'view_background_tasks_tab'
    return_dict["error"] = 'Error retriving background tasks'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_task_details(request,task_id):
  return_dict = {}
  db_path = settings.DATABASES["default"]["NAME"]
  try:
    task_name,err = scheduler_utils.get_background_job(db_path,int(task_id))
    details,err = scheduler_utils.get_task_details(db_path,int(task_id))
    status = ""
    if details[0]['retries'] == -2:
      # This code always updates the 0th element of the command list. This is assuming that we will only have one long running command.
      if os.path.isfile("/tmp/%d.log"%int(task_id)):
        lines,err = command.get_command_output("wc -l /tmp/%d.log"%int(task_id))
        no_of_lines = lines[0].split()[0]
        print no_of_lines
        if int(no_of_lines) <= 41:
          # This code always updates the 0th element of the command list. This is assuming that we will only have one long running command.
          with open('/tmp/%d.log'%int(task_id)) as output:
            status = status + ''.join(output.readlines())
        else:
          first,err = command.get_command_output("head -n 5 /tmp/%d.log"%int(task_id))
          last,err = command.get_command_output("tail -n 20 /tmp/%d.log"%int(task_id))
          status = status + '\n'.join(first)
          status = status + "\n.... \n ....\n"
          status = status + '\n'.join(last)
        
    details[0]['output'] = status
    return_dict["task_name"] = task_name[0]["task_name"]
    return_dict["tasks"] = details
    return django.shortcuts.render_to_response("view_task_details.html", return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "scheduler_base.html"
    return_dict["page_title"] = 'Background jobs'
    return_dict['tab'] = 'view_background_tasks_tab'
    return_dict["error"] = 'Error retriving background task details'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

