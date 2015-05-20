import zipfile, datetime

import django, django.template
from  django.contrib import auth

import integralstor
from integralstor import common, audit, alerts

import integralstor-unicell
from integralstor-unicell import system_info

import integral_view
from integral_view.forms import volume_management_forms, log_management_forms
from integral_view.utils import iv_logging


def edit_integral_view_log_level(request):

  return_dict = {}
  try:
    if request.method == 'POST':
      iv_logging.debug("Trying to change Integral View Log settings")
      form = log_management_forms.IntegralViewLoggingForm(request.POST)
      if form.is_valid():
        iv_logging.debug("Trying to change Integral View Log settings - form valid")
        cd = form.cleaned_data
        log_level = int(cd['log_level'])
        iv_logging.debug("Trying to change Integral View Log settings - log level is %d"%log_level)
        try:
          iv_logging.set_log_level(log_level)
        except Exception, e:
          return_dict['error'] = 'Error setting log level : %s'%e
          return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
        iv_logging.debug("Trying to change Integral View Log settings - changed log level")
        return django.http.HttpResponseRedirect("/show/integral_view_log_level?saved=1")
    else:
      init = {}
      init['log_level'] = iv_logging.get_log_level()
      form = log_management_forms.IntegralViewLoggingForm(initial=init)
      return_dict['form'] = form
      return django.shortcuts.render_to_response('edit_integral_view_log_level.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    if "Another transaction is in progress".lower() in s.lower():
      return_dict["error"] = "An underlying storage operation has locked a volume so we are unable to process this request. Please try after a couple of seconds"
    else:
      return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def download_sys_log(request):
  """ Download the system log of the type specified in sys_log_type POST param for the node specified in the hostname POST parameter. 
  This calls the /sys_log via an http request on that node to get the info"""

  return_dict = {}
  try:
    scl = system_info.load_system_config()
    form = log_management_forms.SystemLogsForm(request.POST or None, system_config_list = scl)
  
    if request.method == 'POST':
      if form.is_valid():
        cd = form.cleaned_data
        try:
          sys_log_type = cd['sys_log_type']
          hostname = cd["hostname"]
        except Exception as e:
          return_dict["error"] = "Insufficient information. Node or log type not specified: %s"%str(e)
          return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
        iv_logging.debug("Got sys log download request for type %s hostname %s"%(sys_log_type, hostname))
  
        fn = {'boot':'/var/log/boot.log', 'dmesg':'/var/log/dmesg', 'message':'/var/log/messages', 'smb':'/var/log/smblog.vfs', 'winbind':'/var/log/samba/log.winbindd','ctdb':'/var/log/log.ctdb'}
        dn = {'boot':'boot.log', 'dmesg':'dmesg', 'message':'messages','smb':'samba_logs','winbind':'winbind_logs','ctdb':'ctdb_logs'}
  
        file_name = fn[sys_log_type]
        display_name = dn[sys_log_type]
  
        import os
        import salt.client
  
        client = salt.client.LocalClient()
  
        ret = client.cmd('%s'%(hostname),'cp.push',[file_name])
  
        # This has been maintained for reference purposes.
        # dt = datetime.datetime.now()
        # dt_str = dt.strftime("%d%m%Y%H%M%S")
  
        # lfn = "/tmp/%s_%s"%(sys_log_type, dt_str)
        # cmd = "/opt/fractal/bin/client %s get_file %s %s"%(hostname, file_name, lfn)
        # print "command is "+cmd
  
        # try :
        #   ret, rc = command.execute_with_rc(cmd)
        # except Exception, e:
        #   return_dict["error"] = "Error retrieving remote log file : %s"%e
        #   return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
        # if rc != 0 :
        #   return_dict["error"] = "Error retrieving remote log file. Retrieval returned an error code of %d"%rc
        #   return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
        zf_name = '%s.zip'%display_name
  
        try:
          zf = zipfile.ZipFile(zf_name, 'w')
          zf.write("/var/cache/salt/master/minions/%s/files/%s"%(hostname,file_name), arcname = display_name)
          zf.close()
        except Exception as e:
          return_dict["error"] = "Error compressing remote log file : %s"%str(e)
          return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
        try:
          response = django.http.HttpResponse()
          response['Content-disposition'] = 'attachment; filename=%s.zip'%(display_name)
          response['Content-type'] = 'application/x-compressed'
          with open(zf_name, 'rb') as f:
            byte = f.read(1)
            while byte:
              response.write(byte)
              byte = f.read(1)
          response.flush()
        except Exception as e:
          return None
  
        return response
  
    # either a get or an invalid form so send back form
    return_dict['form'] = form
    return django.shortcuts.render_to_response('download_sys_log_form.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    if "Another transaction is in progress".lower() in s.lower():
      return_dict["error"] = "An underlying storage operation has locked a volume so we are unable to process this request. Please try after a couple of seconds"
    else:
      return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

  
  
def rotate_log(request, log_type):

  return_dict = {}
  try:
    if log_type == "alerts":
      try:
        alerts.rotate_alerts()
      except Exception, e:
        return_dict["error"] = "Error rotating alerts log: %s"%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
      #return_dict["topic"] = "Logging -> Rotate alerts log"
      return_dict["page_header"] = "Logging"
      return_dict["page_sub_header"] = "Rotate alerts log"
      return_dict["message"] = "Alerts log successfully rotated."
    elif log_type == "audit_trail":
      try:
        audit.rotate_audit_trail()
      except Exception, e:
        return_dict["error"] = "Error rotating audit trail : %s"%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
      #return_dict["topic"] = "Logging -> Rotate alerts log"
      return_dict["page_header"] = "Logging"
      return_dict["page_sub_header"] = "Rotate audit log"
      return_dict["message"] = "Audit trail successfully rotated."
    return django.shortcuts.render_to_response('logged_in_result.html', return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    if "Another transaction is in progress".lower() in s.lower():
      return_dict["error"] = "An underlying storage operation has locked a volume so we are unable to process this request. Please try after a couple of seconds"
    else:
      return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

    if log_type not in ["alerts", "audit_trail"]:
      return_dict["error"] = "Unknown log type" 
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
      
def view_rotated_log_list(request, log_type):

  return_dict = {}
  try:
    if log_type not in ["alerts", "audit_trail"]:
      return_dict["error"] = "Unknown log type" 
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
    l = None
    if log_type == "alerts":
      #return_dict["topic"] = "Logging -> View historical alerts log"
      return_dict["page_header"] = "Logging"
      return_dict["page_sub_header"] = "View historical alerts log"
      l = alerts.get_log_file_list()
    elif log_type == "audit_trail":
      #return_dict["topic"] = "Logging -> View historical audit log"
      return_dict["page_header"] = "Logging"
      return_dict["page_sub_header"] = "View historical audit log"
      l = audit.get_log_file_list()
  
    return_dict["type"] = log_type
    return_dict["log_file_list"] = l
    return django.shortcuts.render_to_response('view_rolled_log_list.html', return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    if "Another transaction is in progress".lower() in s.lower():
      return_dict["error"] = "An underlying storage operation has locked a volume so we are unable to process this request. Please try after a couple of seconds"
    else:
      return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_rotated_log_file(request, log_type):

  return_dict = {}
  try:
    if log_type not in ["alerts", "audit_trail"]:
      return_dict["error"] = "Unknown log type" 
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
    if request.method != "POST":
      return_dict["error"] = "Unsupported request"
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
      
    if "file_name" not in request.POST:
      return_dict["error"] = "Filename not specified"
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
    file_name = request.POST["file_name"]
  
    if log_type == "alerts":
      try:
        l = alerts.load_alerts(file_name)
        return_dict["alerts_list"] = l
        return_dict["historical"] = True
        return django.shortcuts.render_to_response('view_alerts.html', return_dict, context_instance = django.template.context.RequestContext(request))
      except Exception, e:
        return_dict["error"] = str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      try:
        d = audit.get_lines(file_name)
        return_dict["audit_list"] = d
        return_dict["historical"] = True
        return django.shortcuts.render_to_response('view_audit_trail.html', return_dict, context_instance = django.template.context.RequestContext(request))
      except Exception, e:
        return_dict["error"] = str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    if "Another transaction is in progress".lower() in s.lower():
      return_dict["error"] = "An underlying storage operation has locked a volume so we are unable to process this request. Please try after a couple of seconds"
    else:
      return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

  








'''
def sys_log(request, log_type = None):
  """ Invoked by a node in order to deliver the sys log to the remote node.  Shd not normally be called from a browser """

  if not log_type:
    return None

  fn = {'boot':'/var/log/boot.log', 'dmesg':'/var/log/dmesg', 'message':'/var/log/messages'}
  dn = {'boot':'boot.log', 'dmesg':'dmesg', 'message':'messages'}

  file_name = fn[log_type]
  display_name = dn[log_type]
  zf_name = '/tmp/%s'%log_type

  dt = datetime.datetime.now()
  dt_str = dt.strftime("%d%m%Y%H%M%S")
  zf_name = zf_name + dt_str +".zip"
  try:
    zf = zipfile.ZipFile(zf_name, 'w')
    zf.write(file_name, arcname = display_name)
    zf.close()
  except Exception as e:
    return None

  try:
    response = django.http.HttpResponse()
    response['Content-disposition'] = 'attachment; filename=%s%s.zip'%(log_type, dt_str)
    response['Content-type'] = 'application/x-compressed'
    with open(zf_name, 'rb') as f:
      byte = f.read(1)
      while byte:
        response.write(byte)
        byte = f.read(1)
    response.flush()
  except Exception as e:
    return None

  return response


      url = "http://%s:8000/sys_log/%s"%(hostname, sys_log_type)
      d = download.url_download(url)
      if d["error"]:
        return_dict["error"] = d["error"]
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
      
      fn = {'boot':'/var/log/boot.log', 'dmesg':'/var/log/dmesg', 'message':'/var/log/messages'}
      dn = {'boot':'boot.log', 'dmesg':'dmesg', 'message':'messages'}

      file_name = fn[sys_log_type]
      display_name = dn[sys_log_type]
      zf_name = '/tmp/%s'%sys_log_type

      try:
        response = django.http.HttpResponse()
        response['Content-disposition'] = d["content-disposition"]
        response['Content-type'] = 'application/x-compressed'
        response.write(d["content"])
        response.flush()
      except Exception as e:
        return_dict["error"] = "Error requesting log file: %s"%str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))

      return response
'''
