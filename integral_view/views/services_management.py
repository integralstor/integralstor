import django, django.template

import integralstor_common
import integralstor_unicell
from integralstor_common import networking, audit, command

  
def view_services(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'
  
    if "action" in request.GET:
      if request.GET["action"] == "start_success":
        conf = "Service start successful"
      elif request.GET["action"] == "stop_success":
        conf = "Service stop successful"
      elif request.GET["action"] == "stop_fail":
        conf = "Service stop failed"
      elif request.GET["action"] == "start_fail":
        conf = "Service start failed"
      return_dict["conf"] = conf
    services_dict = {}
    services = [('network', 'Networking'), ('ntpd','NTP'), ('smb', 'CIFS - smb'), ('winbind', 'CIFS - winbind'), ('tgtd', 'ISCSI'), ('nfs', 'NFS')]
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
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def change_service_status(request):
  return_dict = {}
  try:
    if request.method == "GET":
      return_dict["error"] = "Invalid request. Please use the menus"
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    if 'service' not in request.POST:
      return_dict["error"] = "Invalid request. Please use the menus"
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    if 'action' not in request.POST or request.POST['action'] not in ['start', 'stop']:
      return_dict["error"] = "Invalid request. Please use the menus"
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    audit_str = "Service status change of %s initiated to %s state."%(request.POST['service'], request.POST['action'])
    d, err = _change_service_status(request.POST['service'], request.POST['action'])
    print d
    if not d:
      audit_str += 'Request failed.'
      audit.audit("change_service_status", audit_str, request.META["REMOTE_ADDR"])
      if err:
        raise Exception(err)
      else:
        raise Exception('An error occurred when changing service status')

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
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def _get_service_status(service):
  d = {}
  try:
    ret, rc = command.execute_with_rc('service %s status'%service[0])
    d['status_code'] = rc
    if rc == 0:
      d['status_str'] = 'Running'
    elif rc == 3:
      d['status_str'] = 'Stopped'
    elif rc == 1:
      d['status_str'] = 'Error'
    d['output_str'] = ''
    out = command.get_output_list(ret)
    if out:
      d['output_str'] += ','.join(out)
    err = command.get_error_list(ret)
    if err:
      d['output_str'] += ','.join(err)
  except Exception, e:
    return None, 'Error retrieving service status : %s'%str(e)
  else:
    return d, None

def _change_service_status(service, action):
  d = {}
  try:
    ret, rc = command.execute_with_rc('service %s %s'%(service, action))
    d['status_code'] = rc
    d['output_str'] = ''
    out = command.get_output_list(ret)
    if out:
      d['output_str'] += ','.join(out)
    err = command.get_error_list(ret)
    if err:
      d['output_str'] += ','.join(err)
  except Exception, e:
    return None, 'Error retrieving service status : %s'%str(e)
  else:
    return d, None

if __name__ == '__main__':
  print _get_service_status(('ntpd', 'NTP'))
  print _get_service_status(('network', 'networking'))
  print _get_service_status(('salt-minion', 'salt-minion'))
