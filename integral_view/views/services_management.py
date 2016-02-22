import django, django.template,os

import subprocess 
import integralstor_common
import integralstor_unicell
from integralstor_common import networking, audit, command,zfs,common,scheduler_utils,ssh
from integralstor_unicell import local_users

  
def view_services(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'
  
    if "action" in request.GET:
      if request.GET["action"] == "start_success":
        conf = "Service start successful. Please wait for a few seconds for the status below to be updated."
      elif request.GET["action"] == "stop_success":
        conf = "Service stop successful. Please wait for a few seconds for the status below to be updated."
      elif request.GET["action"] == "stop_fail":
        conf = "Service stop failed"
      elif request.GET["action"] == "start_fail":
        conf = "Service start failed"
      return_dict["conf"] = conf
    services_dict = {}
    services = [('network', 'Networking'), ('ntpd','NTP'), ('smb', 'CIFS - smb'), ('winbind', 'CIFS - winbind'), ('tgtd', 'ISCSI'), ('nfs', 'NFS'),('vsftpd','FTP')]
    for service in services:
      services_dict[service[0]] = {} 
      services_dict[service[0]]['name'] =  service[1]
      services_dict[service[0]]['service'] =  service[0]
      sd, err = _get_service_status(service)
      if not sd:
        if err:
          services_dict[service[0]]['err'] = err
        else:
          services_dict[service[0]]['err'] = 'Error retrieving status'
      services_dict[service[0]]['info'] = sd

      return_dict["services"] = services_dict
      template = "view_services.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "services_base.html"
    return_dict["page_title"] = 'System services'
    return_dict['tab'] = 'view_services_tab'
    return_dict["error"] = 'Error loading system services status'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def change_service_status(request):
  return_dict = {}
  try:
    if request.method == "GET":
      raise Exception("Invalid request. Please use the menus")
    if 'service' not in request.POST:
      raise Exception("Invalid request. Please use the menus")
    if 'action' not in request.POST or request.POST['action'] not in ['start', 'stop']:
      raise Exception("Invalid request. Please use the menus")
    audit_str = "Service status change of %s initiated to %s state."%(request.POST['service'], request.POST['action'])
    d, err = _change_service_status(request.POST['service'], request.POST['action'])
    if not d:
      audit_str += 'Request failed.'
      audit.audit("change_service_status", audit_str, request.META["REMOTE_ADDR"])
      if err:
        raise Exception(err)
      else:
        raise Exception('Changing service status error')

    if d['status_code'] == 0:
      audit_str += 'Request succeeded.'
    else:
      audit_str += 'Request failed.'
    audit.audit("change_service_status", audit_str, request.META["REMOTE_ADDR"])

    if request.POST['action'] == 'start':
      if d['status_code'] == 0:
        return django.http.HttpResponseRedirect('/view_services?&action=start_success')
      else:
        return django.http.HttpResponseRedirect('/view_services?&action=start_fail')
    elif request.POST['action'] == 'stop':
      if d['status_code'] == 0:
        return django.http.HttpResponseRedirect('/view_services?&action=stop_success')
      else:
        return django.http.HttpResponseRedirect('/view_services?&action=stop_fail')

      
  except Exception, e:
    return_dict['base_template'] = "services_base.html"
    return_dict["page_title"] = 'Modify system service state'
    return_dict['tab'] = 'view_services_tab'
    return_dict["error"] = 'Error modifying system services state'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def upload_ssh_key(request):
  return_dict = {}
  if request.method == 'POST':
    authorized_key = request.FILES.get('pub_key')
    with open('/root/.ssh/authorized_keys', 'wb+') as destination:
        for chunk in authorized_key.chunks():
            destination.write(chunk)
    perm,err = ssh.ssh_dir_permissions()
    return django.shortcuts.render_to_response("add_ssh_key.html", return_dict, context_instance=django.template.context.RequestContext(request))
  elif request.method == 'GET':
    return django.shortcuts.render_to_response("add_ssh_key.html", return_dict, context_instance=django.template.context.RequestContext(request))

def edit_ssh_key(request):
  pass

def list_ssh_keys(request):
  pass

def delete_ssh_keys(request):
  pass

def get_my_ssh_key(request):
  return_dict = {}
  key = ssh.get_ssh_key() 
  if key:
    ssh.generate_ssh_key()
  key = ssh.get_ssh_key()
  return_dict['key'] = key
  return django.shortcuts.render_to_response("show_my_ssh_key.html", return_dict, context_instance=django.template.context.RequestContext(request))

def regenerate_ssh_key(request):
  return_dict = {}
  key = ssh.generate_new_ssh_key() 
  return_dict['my_ssh_key'] = key
  return django.shortcuts.render_to_response("show_my_ssh_key.html", return_dict, context_instance=django.template.context.RequestContext(request))


def _get_service_status(service):
  d = {}
  try:
    (ret, rc), err = command.execute_with_rc('service %s status'%service[0])
    if err:
      raise Exception(err)
    d['status_code'] = rc
    if rc == 0:
      d['status_str'] = 'Running'
    elif rc == 3:
      d['status_str'] = 'Stopped'
    elif rc == 1:
      d['status_str'] = 'Error'
    d['output_str'] = ''
    out, err = command.get_output_list(ret)
    if err:
      raise Exception(err)
    if out:
      d['output_str'] += ','.join(out)
    err, e = command.get_error_list(ret)
    if e:
      raise Exception(e)
    if err:
      d['output_str'] += ','.join(err)
  except Exception, e:
    return None, 'Error retrieving service status : %s'%str(e)
  else:
    return d, None

def _change_service_status(service, action):
  d = {}
  try:
    #ret, rc = command.execute_with_rc('service %s %s'%(service, action))
    cmd = {'%s %s'%(service, action):'service %s %s'%(service, action)}
    cmd_list= [cmd]
    task_name = "%s %s"%(service,action)
    db_path,err = common.get_db_path()
    status,err = scheduler_utils.schedule_a_job(db_path,task_name,cmd_list)
    if not err:
      d['output_str'] = 'Scheduled for restart'
      d['status_code'] = 0 
    else:
      d['output_str'] = 'Schedule failed. Please try again'
      d['status_code'] = -1
  except Exception, e:
    return None, 'Error retrieving service status : %s'%str(e)
  else:
    return d, None

def _reboot_system(action):
  d = {}
  try:
    ret, rc = command.execute_with_rc(action)
    if not err:
      d['output_str'] = 'Scheduled for restart'
      d['status_code'] = 0 
    else:
      d['output_str'] = 'Schedule failed. Please try again'
      d['status_code'] = -1
  except Exception, e:
    return None, 'Error retrieving service status : %s'%str(e)
  else:
    return d, None


## This is a lot of hack inside just to get it work. Re-write when rewriting the architecture.
def start_ftp_service(request):
  return_dict = {}
  try:
    if request.method == "POST":
      dataset = request.POST.get('dataset')
      f = open('/opt/integralstor/ftp','w')
      f.write(dataset)
      f.close() 
      users,err = local_users.get_local_users() 
      if not os.path.exists('/etc/vsftpd/users'):
        os.makedirs('/etc/vsftpd/users')
      for user in users:
        user_path = '/etc/vsftpd/users/%s'%(user['username'])
        f = open(user_path,'w')
        f.write("#AutoGenerated by IntegralStor. Individual user permission for vsftpd. Do not change this file manually \n")
        f.write('local_root=%s\n'%(dataset+"/"+user['username']))
        f.write('dirlist_enable=YES\n')
        f.write('download_enable=YES\n')
        f.write('write_enable=YES\n')
        if not os.path.exists(dataset+"/"+user['username']):
          os.makedirs(dataset+"/"+user['username'])
        os.chown(dataset+"/"+user['username'],user['uid'],user['gid'])
      audit_str = "Service status change of vsftpd initiated to start state."
      d, err = _change_service_status('vsftpd','start')
      if not d:
        audit_str += 'Request failed.'
        audit.audit("change_service_status", audit_str, request.META["REMOTE_ADDR"])
        if err:
          raise Exception(err)
        else:
          raise Exception('Changing service status error')
      if d['status_code'] == 0:
        audit_str += 'Request succeeded.'
        return django.http.HttpResponseRedirect('/view_services?&action=start_success')
      else:
        audit_str += 'Request failed.'
        return django.http.HttpResponseRedirect('/view_services?&action=start_fail')
      audit.audit("change_service_status", audit_str, request.META["REMOTE_ADDR"])
  except Exception, e:
    return_dict['base_template'] = "services_base.html"
    return_dict["page_title"] = 'Start FTP service'
    return_dict['tab'] = 'ftp_service_settings'
    return_dict["error"] = 'Create a dataset before starting the FTP service'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
  else:
    try:
      pools, err = zfs.get_pools()
      ds_list = []
      for pool in pools:
        for ds in pool["datasets"]:
          if ds['properties']['type']['value'] == 'filesystem':
            ds_list.append({'name': ds["name"], 'mountpoint': ds["mountpoint"]})
      if not ds_list:
        raise Exception('No ZFS datasets available. Please create a dataset before starting a FTP service.')
      if not err:
        return_dict["datasets"] = ds_list
        if os.path.isfile('/opt/integralstor/ftp'):
          with open('/opt/integralstor/ftp','r') as f:
            return_dict["selected"] = f.read()
        else:
          return_dict["first_time"] = "FTP service is not configured with dataset."
      else:
        return_dict["datasets"] = {}
      template = "start_ftp_service.html"
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
    except Exception, e:
      return_dict['base_template'] = "services_base.html"
      return_dict["page_title"] = 'Start FTP service'
      return_dict['tab'] = 'ftp_service_settings'
      return_dict["error"] = 'Create a dataset before starting the FTP service'
      return_dict["error_details"] = str(e)
      return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
      
def reboot(request):
  return_dict = {}
  audit_str = ""
  if request.method == "POST":
    try:
      d, err = _reboot_system('reboot')
      if not d:
        audit_str += 'Request failed.'
        audit.audit("Rebooting System", audit_str, request.META["REMOTE_ADDR"])
        if err:
          raise Exception(err)
        else:
          raise Exception('Reboot Scheduling Error')

      if d['status_code'] == 0:
        audit_str += 'Reboot Succeeded succeeded.'
      else:
        audit_str += 'Request failed.'
      audit.audit("Reboot ", audit_str, request.META["REMOTE_ADDR"])
      return django.shortcuts.render_to_response("reboot.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
      return_dict['base_template'] = "admin_base.html"
      return_dict["page_title"] = 'Reboot'
      return_dict['tab'] = 'reboot'
      return_dict["error"] = 'Reboot Happening. Please Wait ...!'
      return_dict["error_details"] = str(e)
      return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

  if request.method == "GET":
    return django.shortcuts.render_to_response("reboot.html", return_dict, context_instance=django.template.context.RequestContext(request))
     

if __name__ == '__main__':
  print _get_service_status(('ntpd', 'NTP'))
  print _get_service_status(('network', 'networking'))
  print _get_service_status(('salt-minion', 'salt-minion'))
