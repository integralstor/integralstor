import django.template, django
from django.conf import settings
from django.contrib.auth.decorators import login_required
import django.http 

import os, os.path
from integralstor_common import scheduler_utils, common, command, zfs

def view_scheduled_jobs(request):
  return_dict = {}
  try:
    cron_jobs,err = scheduler_utils.get_all_cron_jobs()
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
  try:
    cron_name = request.POST.get('cron_name')
    response['Content-disposition'] = 'attachment; filename='+cron_name.replace(" ","_")+'.log'
    response['Content-type'] = 'application/x-compressed'
    log_folder_path, err = common.get_log_folder_path()
    if err:
      raise Exception(err)
    with open(log_folder_path+"/"+cron_name.replace(" ","_")+".log", 'rb') as f:
      byte = f.read(1)
      while byte:
        response.write(byte)
        byte = f.read(1)
        response.flush()
  except Exception as e:
    return django.http.HttpResponse(e)
  else:
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
    if "ack" in request.GET:
      if request.GET["ack"] == "deleted":
        return_dict['ack_message'] = "Background task successfully removed"
    return_dict["back_jobs"] = scheduler_utils.get_background_jobs(db_path)[0]
    return django.shortcuts.render_to_response("view_background_tasks.html", return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "scheduler_base.html"
    return_dict["page_title"] = 'Background tasks'
    return_dict['tab'] = 'view_background_tasks_tab'
    return_dict["error"] = 'Error retriving background tasks'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def remove_background_task(request):
  return_dict = {}
  try:
    if 'task_id' not in request.REQUEST:
      raise Exception('Invalid request. Please use the menus.')
    ret, err = scheduler_utils.remove_task(request.REQUEST['task_id'])
    if err:
      raise Exception(err)
    return django.http.HttpResponseRedirect('/view_background_tasks?ack=deleted')
  except Exception, e:
    return_dict['base_template'] = "scheduler_base.html"
    return_dict["page_title"] = 'Background tasks'
    return_dict['tab'] = 'view_background_tasks_tab'
    return_dict["error"] = 'Error removing background task'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_task_details(request,task_id):
  return_dict = {}
  db_path = settings.DATABASES["default"]["NAME"]
  try:
    task_name,err = scheduler_utils.get_background_job(db_path,int(task_id))
    return_dict['task_id'] = task_id
    details,err = scheduler_utils.get_task_commands(db_path,int(task_id))
    status = ""
    if details[0]['retries'] == -2:
      # This code always updates the 0th element of the command list. This is assuming that we will only have one long running command.
      if os.path.isfile("/tmp/%d.log"%int(task_id)):
        lines,err = command.get_command_output("wc -l /tmp/%d.log"%int(task_id))
        no_of_lines = lines[0].split()[0]
        #print no_of_lines
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
    return_dict["commands"] = details
    return django.shortcuts.render_to_response("view_task_details.html", return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "scheduler_base.html"
    return_dict["page_title"] = 'Background jobs'
    return_dict['tab'] = 'view_background_tasks_tab'
    return_dict["error"] = 'Error retriving background task details'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

