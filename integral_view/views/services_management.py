import django, django.template,os

import subprocess, urllib 
import integralstor_common
import integralstor_unicell
from integralstor_common import networking, audit, command,zfs,common,scheduler_utils, services_management
from integralstor_unicell import local_users

  
def view_services(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'
  
    if "ack" in request.GET:
      if request.GET["ack"] == "start_success":
        return_dict['ack_message'] = "Service start successful. Please wait for a few seconds for the status below to be updated."
      elif request.GET["ack"] == "stop_success":
        return_dict['ack_message'] = "Service stop successful. Please wait for a few seconds for the status below to be updated."
      elif request.GET["ack"] == "stop_fail":
        return_dict['ack_message'] = "Service stop failed"
      elif request.GET["ack"] == "start_fail":
        return_dict['ack_message'] = "Service start failed"
    if 'service_change_status' in request.GET:
      if request.GET['service_change_status'] != 'none':
        return_dict['ack_message'] = 'Service status change initiated. Output : %s'%urllib.quote(request.GET['service_change_status'])
      else:
        return_dict['ack_message'] = 'Service status change initiated'

    services_dict = {}
    services = [('network', 'Networking'), ('ntpd','NTP'), ('smb', 'CIFS - smb'), ('winbind', 'CIFS - winbind'), ('tgtd', 'ISCSI'), ('nfs', 'NFS'),('vsftpd','FTP'),('shellinaboxd','Shell Access')]
    for service in services:
      services_dict[service[0]] = {} 
      services_dict[service[0]]['name'] =  service[1]
      services_dict[service[0]]['service'] =  service[0]
      sd, err = services_management.get_service_status(service)
      if not sd:
        if err:
          services_dict[service[0]]['err'] = err
        else:
          services_dict[service[0]]['err'] = 'Error retrieving status'
      services_dict[service[0]]['info'] = sd

    return_dict["services"] = services_dict
    return django.shortcuts.render_to_response('view_services.html', return_dict, context_instance = django.template.context.RequestContext(request))
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

    service = request.POST['service']
    action = request.POST['action']

    if 'action' == 'start' and service == 'vsftpd':
      #Need to make sure that all local users have their directories created so do it..
      config, err = vsftp.get_ftp_config()
      if err:
        raise Exception(err)
      users,err = local_users.get_local_users()
      if err:
        raise Exception(err)
      ret, err = create_ftp_user_dirs(config['dataset'], users)
      if err:
        raise Exception(err)

    audit_str = "Service status change of %s initiated to %s state."%(service, action)
    audit.audit("change_service_status", audit_str, request.META)

    out, err = services_management.change_service_status(service, action)
    if err:
      raise Exception(err)

    if out:
      return django.http.HttpResponseRedirect('/view_services?&service_change_status=%s'%','.join(out))
    else:
      return django.http.HttpResponseRedirect('/view_services?service_change_status=none')
    
  except Exception, e:
    return_dict['base_template'] = "services_base.html"
    return_dict["page_title"] = 'Modify system service state'
    return_dict['tab'] = 'view_services_tab'
    return_dict["error"] = 'Error modifying system services state'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))



'''
DEPRECATED - NOT USED ANYMORE - FUNCTIONALITY MOVED TO ftp_management.py

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
        audit.audit("change_service_status", audit_str, request.META)
        if err:
          raise Exception(err)
        else:
          raise Exception('Changing service status error')
      if d['status_code'] == 0:
        audit_str += 'Request succeeded.'
        return django.http.HttpResponseRedirect('/view_services?&ack=start_success')
      else:
        audit_str += 'Request failed.'
        return django.http.HttpResponseRedirect('/view_services?&ack=start_fail')
      audit.audit("change_service_status", audit_str, request.META)
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

'''
      
     

if __name__ == '__main__':
  print _get_service_status(('ntpd', 'NTP'))
  print _get_service_status(('network', 'networking'))
  print _get_service_status(('salt-minion', 'salt-minion'))
