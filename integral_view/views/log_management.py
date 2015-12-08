import zipfile, datetime,os,shutil

import django, django.template
from  django.contrib import auth
from django.core.files.storage import default_storage

from integralstor_common import common, audit, alerts

from integralstor_unicell import system_info

import integral_view
from integral_view.forms import log_management_forms,common_forms
from integral_view.utils import iv_logging


def handle_uploaded_file(f):
  with open('/tmp/upload.zip', 'wb+') as destination:
    for chunk in f.chunks():
      destination.write(chunk)
  return True,"/tmp/upload.zip"

def copy_and_overwrite(from_path, to_path):
  if os.path.exists(to_path):
    shutil.rmtree(to_path)
  shutil.copytree(from_path, to_path)
  return True

def copy_file_and_overwrite(from_path,to_path):
  shutil.copyfile(from_path,to_path)
  return True

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
        ret, err = iv_logging.set_log_level(log_level)
        if err:
          raise Exception(err)
        iv_logging.debug("Trying to change Integral View Log settings - changed log level")
        return django.http.HttpResponseRedirect("/show/integral_view_log_level?saved=1")
    else:
      init = {}
      init['log_level'] = iv_logging.get_log_level()
      form = log_management_forms.IntegralViewLoggingForm(initial=init)
      return_dict['form'] = form
      return django.shortcuts.render_to_response('edit_integral_view_log_level.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "logging_base.html"
    return_dict["page_title"] = 'Modify IntegralView log level'
    return_dict['tab'] = 'view_current_audit_tab'
    return_dict["error"] = 'Error modifying IntegralView log level'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def download_sys_log(request):
  """ Download the system log of the type specified in sys_log_type POST param for the node specified in the hostname POST parameter. 
  This calls the /sys_log via an http request on that node to get the info"""

  return_dict = {}
  try:
    scl, err = system_info.load_system_config()
    if err:
      raise Exception(err)
    form = log_management_forms.SystemLogsForm(request.POST or None, system_config_list = scl)
  
    if request.method == 'POST':
      if form.is_valid():
        cd = form.cleaned_data
        sys_log_type = cd['sys_log_type']
        hostname = cd["hostname"]
  
        iv_logging.debug("Got sys log download request for type %s hostname %s"%(sys_log_type, hostname))
  
        fn = {'boot':'/var/log/boot.log', 'dmesg':'/var/log/dmesg', 'message':'/var/log/messages', 'smb':'/var/log/smblog.vfs', 'winbind':'/var/log/samba/log.winbindd','ctdb':'/var/log/log.ctdb'}
        dn = {'boot':'boot.log', 'dmesg':'dmesg', 'message':'messages','smb':'samba_logs','winbind':'winbind_logs','ctdb':'ctdb_logs'}
  
        file_name = fn[sys_log_type]
        display_name = dn[sys_log_type]
  
        import os

        use_salt, err = common.use_salt()
        if err:
          raise Exception(err)
        if use_salt:
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
          if use_salt:
            zf.write("/var/cache/salt/master/minions/%s/files/%s"%(hostname,file_name), arcname = display_name)
          else:
            zf.write(file_name, arcname = display_name)
          zf.close()
        except Exception as e:
          raise Exception("Error compressing remote log file : %s"%str(e))
  
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
    return_dict['base_template'] = "logging_base.html"
    return_dict["page_title"] = 'Download system logs'
    return_dict['tab'] = 'download_system_logs_tab'
    return_dict["error"] = 'Error downloading system logs'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

  
  
def rotate_log(request, log_type=None):
  return_dict = {}
  try:
    if log_type not in ["alerts", "audit_trail"]:
      raise Exception("Unknown log type")
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
    if log_type == "alerts":
      return_dict['tab'] = 'view_current_alerts_tab'
      return_dict["page_title"] = 'Rotate system alerts log'
      ret, err = alerts.rotate_alerts()
      if err:
        raise Exception(err)
      return_dict["message"] = "Alerts log successfully rotated."
      return django.http.HttpResponseRedirect("/view_rotated_log_list/alerts?success=true")
    elif log_type == "audit_trail":
      return_dict['tab'] = 'view_current_audit_tab'
      return_dict["page_title"] = 'Rotate system audit trail'
      ret, err = audit.rotate_audit_trail()
      if err:
        raise Exception(err)
      return_dict["message"] = "Audit trail successfully rotated."
      return django.http.HttpResponseRedirect("/view_rotated_log_list/audit_trail/?success=true")
  except Exception, e:
    return_dict['base_template'] = "logging_base.html"
    return_dict["error"] = 'Error rotating log'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

  
def download_sys_info(request):
  return_dict = {}
  try:
    display_name, err = common.get_platform_root()
    print display_name
    if err:
      raise Exception(err)
    zf_name = "system_info.zip"
    try:
      zf = zipfile.ZipFile(zf_name, 'w')
      abs_src = os.path.abspath(display_name)
      for dirname, subdirs, files in os.walk(display_name):
        if "config" in dirname:
          for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            zf.write(absname, arcname)
      logs = {'boot':'/var/log/boot.log', 'dmesg':'/var/log/dmesg', 'message':'/var/log/messages', 'smb':'/var/log/smblog.vfs', 'winbind':'/var/log/samba/log.winbindd','ctdb':'/var/log/log.ctdb','smb_conf':'/etc/samba/smb.conf','ntp_conf':'/etc/ntp.conf','krb5_conf':'/etc/krb5.conf'}
      for key,value in logs.iteritems():
          print value
          if os.path.isfile(value):
            zf.write(value, key)
      zf.close()
    except Exception as e:
      raise Exception("Error compressing remote log file : %s"%str(e))
    response = django.http.HttpResponse()
    response['Content-disposition'] = 'attachment; filename=system_info.zip'
    response['Content-type'] = 'application/x-compressed'
    with open(zf_name, 'rb') as f:
      byte = f.read(1)
      while byte:
        response.write(byte)
        byte = f.read(1)
    response.flush()
    return response
  except Exception as e:
    return_dict['base_template'] = "logging_base.html"
    return_dict["page_title"] = 'Download system information'
    return_dict['tab'] = 'node_info_tab'
    return_dict["error"] = 'Error downloading system information'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def upload_sys_info(request):
  return_dict = {}
  try:
    if request.method == "POST" :
      status,path = handle_uploaded_file(request.FILES['file_field'])
      if path:
        print path
        zip = zipfile.ZipFile(path,'r')
        data = zip.namelist()
        move = zip.extractall("/tmp/upload/")
        logs = {'boot':'/var/log/boot.log', 'dmesg':'/var/log/dmesg', 'message':'/var/log/messages', 'smb':'/var/log/smblog.vfs', 'winbind':'/var/log/samba/log.winbindd','ctdb':'/var/log/log.ctdb','smb_conf':'/etc/samba/smb.conf','ntp_conf':'/etc/ntp.conf','krb5_conf':'/etc/krb5.conf'}
        for key,value in logs.iteritems():
          if key and os.path.isfile(key):
            copy_file_and_overwrite("/tmp/upload/"+key,value)
        copy_and_overwrite("/tmp/upload/config",common.get_config_dir()[0])
        return django.http.HttpResponseRedirect("/show/node_info/")
    else:
      form = common_forms.FileUploadForm()
      return_dict["form"] = form  
      return django.shortcuts.render_to_response("upload_sys_info.html", return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception,e:
    return_dict['base_template'] = "logging_base.html"
    return_dict["error"] = 'Error displaying rotated log list'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
   

def view_rotated_log_list(request, log_type):

  return_dict = {}
  try:
    if log_type not in ["alerts", "audit_trail"]:
      raise Exception("Unknown log type")
    l = None
    if log_type == "alerts":
      return_dict["page_title"] = 'View rotated alerts logs'
      return_dict['tab'] = 'view_rotated_alert_log_list_tab'
      return_dict["page_header"] = "Logging"
      return_dict["page_sub_header"] = "View historical alerts log"
      l, err = alerts.get_log_file_list()
      if err:
        raise Exception(err)
    elif log_type == "audit_trail":
      return_dict["page_title"] = 'View rotated audit trail logs'
      return_dict['tab'] = 'view_rotated_audit_log_list_tab'
      return_dict["page_header"] = "Logging"
      return_dict["page_sub_header"] = "View historical audit log"
      l, err = audit.get_log_file_list()
      if err:
        raise Exception(err)
  
    return_dict["type"] = log_type
    return_dict["log_file_list"] = l
    return django.shortcuts.render_to_response('view_rolled_log_list.html', return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "logging_base.html"
    return_dict["error"] = 'Error displaying rotated log list'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_rotated_log_file(request, log_type):

  return_dict = {}
  try:
    return_dict['tab'] = 'view_rotated_alert_log_list_tab'
    if log_type not in ["alerts", "audit_trail"]:
      raise Exception("Unknown log type")
  
    if request.method != "POST":
      raise Exception("Unsupported request")
      
    if "file_name" not in request.POST:
      raise Exception("Filename not specified")
  
    file_name = request.POST["file_name"]
  
    return_dict["historical"] = True
    if log_type == "alerts":
      return_dict['tab'] = 'view_rotated_alert_log_list_tab'
      l, err = alerts.load_alerts(file_name)
      if err:
        raise Exception(err)
      return_dict["alerts_list"] = l
      return django.shortcuts.render_to_response('view_alerts.html', return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      return_dict['tab'] = 'view_rotated_audit_log_list_tab'
      d, err = audit.get_lines(file_name)
      if err:
        raise Exception(err)
      return_dict["audit_list"] = d
      return django.shortcuts.render_to_response('view_audit_trail.html', return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "logging_base.html"
    return_dict["page_title"] = 'View rotated log file'
    return_dict["error"] = 'Error viewing rotated log file'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

