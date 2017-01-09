import django.template, django
from django.conf import settings
from django.contrib.auth.decorators import login_required
import django.http 

import os, os.path
from integralstor_common import scheduler_utils, common, command, zfs, db, audit

def view_scheduled_jobs(request):
  return_dict = {}
  try:
    cron_jobs,err = scheduler_utils.get_cron_tasks()
    if err:
      raise Exception(err)
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
  return_dict = {}
  try:
    cron_name = request.POST.get('cron_name')
    # TOFIX
    # removing a cron job doesn't remove the relevant entry from remote_replications table 
    #cmd = "select * from remote_replications where cron_task_id=%s"%cron_name
    #replication,err = db.read_single_row(db_path,cmd)
    #if err:
    #  raise Exception(err)
    #if replication:
      

    delete,err = scheduler_utils.remove_cron(int(cron_name))
    if err:
      raise Exception(err)
    if delete:
      return django.http.HttpResponseRedirect("/view_scheduled_jobs")
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
  try:
    if "ack" in request.GET:
      if request.GET["ack"] == "deleted":
        return_dict['ack_message'] = "Background task successfully removed"
    tasks, err = scheduler_utils.get_tasks()
    if err:
      raise Exception(err)
    return_dict["tasks"] = tasks
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
    
    db_path, err = common.get_db_path ()
    if err:
      raise Exception (err)
    task_description, err = db.get_task_description (db_path, "tasks", "task_id", int(request.REQUEST['task_id']), get_status = True)
    if err:
      task_description = err
    elif task_description is None:
      task_description = "No description found for task with task_id %d" %(request.REQUEST['task_id'])	

    audit.audit("remove_background_task", task_description, request.META)

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
  try:
    task,err = scheduler_utils.get_task(int(task_id))
    if err:
      raise Exception(err)
    return_dict['task'] = task
    subtasks,err = scheduler_utils.get_subtasks(int(task_id))
    if err:
      raise Exception(err)
    return_dict["subtasks"] = subtasks
    #print subtasks, err
    task_output = ""
    log_path, err = common.get_log_folder_path()
    if err:
      raise Exception(err)
    log_dir = '%s/task_logs'%log_path
    log_file_path = '%s/%d.log'%(log_dir, int(task_id))
    if os.path.isfile(log_file_path):
      lines,err = command.get_command_output("wc -l %s"%log_file_path)
      no_of_lines = lines[0].split()[0]
      #print no_of_lines
      if int(no_of_lines) <= 41:
        # This code always updates the 0th element of the command list. This is assuming that we will only have one long running command.
        with open(log_file_path) as output:
          task_output = task_output + ''.join(output.readlines())
      else:
        first,err = command.get_command_output("head -n 5 %s"%log_file_path, shell=True)
        if err:
          print err
        last,err = command.get_command_output("tail -n 20 %s"%log_file_path, shell=True)
        if err:
          print err
        #print last
        task_output = task_output + '\n'.join(first)
        task_output = task_output + "\n.... \n ....\n"
        task_output = task_output + '\n'.join(last)
    return_dict['task_output'] = task_output
        
    return django.shortcuts.render_to_response("view_task_details.html", return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "scheduler_base.html"
    return_dict["page_title"] = 'Background jobs'
    return_dict['tab'] = 'view_background_tasks_tab'
    return_dict["error"] = 'Error retriving background task details'
    return_dict["error_details"] = e
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

