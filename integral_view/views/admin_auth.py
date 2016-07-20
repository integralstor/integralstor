
import django
import django.template
from django.contrib import auth
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required

import os, time, datetime

import integral_view
from integral_view.forms import admin_forms, pki_forms
from integral_view.utils import iv_logging

import integralstor_unicell
from integralstor_unicell import system_info

import integralstor_common
from integralstor_common import audit, mail, common, certificates, nginx,command


def login(request):

  """ Used to login a user into the management utility"""

  try:
    return_dict = {}
    authSucceeded = False

    if request.method == 'POST':
      iv_logging.info("Login request posted")
      # Someone is submitting info so check it
      form = admin_forms.LoginForm(request.POST)
      if form.is_valid():
        # submitted form is valid so now try to authenticate
        # if not valid then fall out to end of function and return form to user
        # with existing data
        cd = form.cleaned_data
        username = cd['username']
        password = cd['password']
        # Try to authenticate
        user = django.contrib.auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
          production, err = integralstor_common.common.is_production()
          if err:
            raise Exception(err)
          '''
          if production:
            # Clear the session if the user has been logged in anywhere else.
            sessions = Session.objects.all()
            for s in sessions:
              if s.get_decoded() and (s.get_decoded()['_auth_user_id'] == user.id):
                s.delete()
          '''
          # authentication succeeded! Login and send to home screen
          django.contrib.auth.login(request, user)
          iv_logging.info("Login request from user '%s' succeeded"%username)
          authSucceeded = True
        else:
          iv_logging.info("Login request from user '%s' failed"%username)
          return_dict['invalidUser'] = True
      else:
        #Invalid form
        iv_logging.debug("Invalid login information posted")
    else:
      # GET request so create a new form and send back to user
      form = admin_forms.LoginForm()
      # Clear the session if the user has been logged in anywhere else.
      sessions = Session.objects.all()
      for s in sessions:
        if s.get_decoded() is not None and s.get_decoded().get('_auth_user_id') is not None:
          return_dict['session_active'] = True

    return_dict['form'] = form

    if authSucceeded:
      return django.http.HttpResponseRedirect('/dashboard/dashboard')

    # For all other cases, return to login screen with return_dict 
    # appropriately populated
    return django.shortcuts.render_to_response('login_form.html', return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))



def logout(request):
  """ Used to logout a user into the management utility"""
  try:
    iv_logging.info("User '%s' logged out"%request.user)
    # Clear the session if the user has been logged in anywhere else.
    sessions = Session.objects.all()
    for s in sessions:
     if s.get_decoded() and (s.get_decoded()['_auth_user_id'] == request.user.id or not s.get_decoded()):
        s.delete()
    django.contrib.auth.logout(request)
    return django.http.HttpResponseRedirect('/login/')
  except Exception, e:
    return_dict['base_template'] = "dashboard_base.html"
    return_dict["page_title"] = 'Logout'
    return_dict['tab'] = 'disks_tab'
    return_dict["error"] = 'Error logging out'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))


def change_admin_password(request):
  """ Used to change a user's password for the management utility"""

  try:
    return_dict = {}

    if request.user and request.user.is_authenticated():
      if request.method == 'POST':
        iv_logging.debug("Admin password change posted")
        #user has submitted the password info
        form = admin_forms.ChangeAdminPasswordForm(request.POST)
        if form.is_valid():
          cd = form.cleaned_data
          oldPasswd = cd['oldPasswd']
          newPasswd1 = cd['newPasswd1']
          newPasswd2 = cd['newPasswd2']
          #Checking for old password is done in the form itself
          if request.user.check_password(oldPasswd):
            if newPasswd1 == newPasswd2:
              # all systems go so now change password
              request.user.set_password(newPasswd1);
              request.user.save()
              return_dict['ack_message'] = 'Password changed sucessful.'
              iv_logging.info("Admin password change request successful.")
              audit_str = "Changed admin password"
              audit.audit("modify_admin_password", audit_str, request.META["REMOTE_ADDR"])
            else:
  	          return_dict['error'] = 'New passwords do not match'
        # else invalid form or error so existing form data to return_dict and 
        # fall through to redisplay the form
        if 'success' not in return_dict:
          return_dict['form'] = form
          iv_logging.info("Admin password change request failed.")
      else:
        form = admin_forms.ChangeAdminPasswordForm()
        return_dict['form'] = form
  
      return django.shortcuts.render_to_response('change_admin_password_form.html', return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      #User not authenticated so return a login screen
      return django.http.HttpResponseRedirect('/login/')
  except Exception, e:
    return_dict['base_template'] = "admin_base.html"
    return_dict["page_title"] = 'Change admininistrator password'
    return_dict['tab'] = 'change_admin_pswd_tab'
    return_dict["error"] = 'Error changing administrator password'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))

def view_system_info(request):
  return_dict = {}
  try:
    si,err = system_info.load_system_config()
    if err:
      raise Exception(err)
    now = datetime.datetime.now()
    milliseconds =  int(time.mktime(time.localtime())*1000)
    return_dict['date_str'] = now.strftime("%A %d %B %Y")
    return_dict['time'] = now
    return_dict['milliseconds'] = milliseconds
    return_dict['system_info'] = si
    if "from" in request.GET:
      frm = request.GET["from"]
      return_dict['frm'] = frm
    return_dict['node'] = si[si.keys()[0]]
    return django.shortcuts.render_to_response("view_system_info.html", return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "system_base.html"
    return_dict["page_title"] = 'System configuration'
    return_dict['tab'] = 'node_info_tab'
    return_dict["error"] = 'Error loading system configuration'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))


def view_email_settings(request):
  return_dict = {}
  try:
    d, err = mail.load_email_settings()
    if err:
      raise Exception(err)
    if not d:
      return_dict["email_not_configured"] = True
    else:
      if d["tls"]:
        d["tls"] = True
      else:
        d["tls"] = False
      if d["email_alerts"]:
        d["email_alerts"] = True
      else:
        d["email_alerts"] = False
      return_dict["email_settings"] = d
    if "ack" in request.REQUEST and request.REQUEST['ack'] == 'saved':
      return_dict["ack_message"] = 'Email settings have successfully been updated.'
    if "err" in request.REQUEST:
      return_dict["err"] = request.REQUEST["err"]
    if "sent_mail" in request.REQUEST:
      return_dict["sent_mail"] = request.REQUEST["sent_mail"]
    return django.shortcuts.render_to_response('view_email_settings.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "system_base.html"
    return_dict["page_title"] = 'View email notification settings'
    return_dict['tab'] = 'email_tab'
    return_dict["error"] = 'Error viewing email notification settings'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
def configure_email_settings(request):

  try:
    return_dict = {}
    url = "edit_email_settings.html"
    if request.method=="GET":
      d, err = mail.load_email_settings()
      if err:
        raise Exception(err)
      if not d:
        form = admin_forms.ConfigureEmailForm()
      else:
        if 'tls' in d and d["tls"]:
          d["tls"] = True
        else:
          d["tls"] = False
        if 'email_alerts' in d and d["email_alerts"]:
          d["email_alerts"] = True
        else:
          d["email_alerts"] = False
        form = admin_forms.ConfigureEmailForm(initial = {'server':d["server"], 'port':d["port"], 'tls':d["tls"], 'username':d["username"], 'email_alerts':d["email_alerts"],'email_audit':d['email_audit'], 'rcpt_list':d["rcpt_list"],'pswd':""})
    else:
      form = admin_forms.ConfigureEmailForm(request.POST)
      if form.is_valid():
        cd = form.cleaned_data
        #print "Saving : "
        ret, err = mail.save_email_settings(cd)
        if err:
          raise Exception(err)

        ret, err = mail.send_mail(cd["server"], cd["port"], cd["username"], cd["pswd"], cd["tls"], cd["rcpt_list"], "Test email from IntegralStor", "This is a test email sent by the IntegralStor system in order to confirm that your email settings are working correctly.")
        if err:
          raise Exception(err)
        if ret:
          return django.http.HttpResponseRedirect("/view_email_settings?ack=saved&sent_mail=1")
        else:
          return django.http.HttpResponseRedirect("/view_email_settings?ack=saved&err=%s"%err)
    return_dict["form"] = form
    return django.shortcuts.render_to_response(url, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "system_base.html"
    return_dict["page_title"] = 'Change email notification settings'
    return_dict['tab'] = 'email_tab'
    return_dict["error"] = 'Error changing email notification settings'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))

def view_https_mode(request):

  return_dict = {}

  try:
    mode, err = nginx.get_nginx_access_mode()
    if err:
      raise Exception(err)

    if "ack" in request.GET:
      if request.GET["ack"] == "set_to_secure":
        return_dict['ack_message'] = "The IntegralView access mode has been successfully set to secure(HTTPS). The server has been scheduled to restart. Please change your browser to access IntegralView using https://<integralview_ip_address>"
      elif request.GET["ack"] == "set_to_nonsecure":
        return_dict['ack_message'] = "The IntegralView access mode has been successfully set to non-secure(HTTP). The server has been scheduled to restart. Please change your browser to access IntegralView using http://<integralview_ip_address>"

    return_dict['port'] = mode['port']
    return django.shortcuts.render_to_response('view_https_mode.html', return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "admin_base.html"
    return_dict["page_title"] = 'Integralview access mode'
    return_dict['tab'] = 'https_tab'
    return_dict["error"] = 'Error loading IntegralView access mode'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def edit_https_mode(request):

  return_dict = {}

  try:

    if 'change_to' not in request.REQUEST:
      raise Exception("Invalid request. Please use the menus")
    change_to = request.REQUEST['change_to']
    return_dict['change_to'] = change_to

    cert_list, err = certificates.get_certificates()
    if err:
      raise Exception(err)
    if not cert_list:
      raise Exception('No certificates have been created. Please create a certificate/key pair before you change the access method')

    if request.method == "GET":
      if change_to == 'secure':
        form = pki_forms.SetHttpsModeForm(cert_list = cert_list)
        return_dict['form'] = form
        return django.shortcuts.render_to_response("edit_https_mode.html", return_dict, context_instance = django.template.context.RequestContext(request))
      else:
        return_dict['conf_message'] = 'Are you sure you want to disable the secure access mode for IntegralView?'
        return django.shortcuts.render_to_response("set_http_mode_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      if change_to == 'secure':
        form = pki_forms.SetHttpsModeForm(request.POST, cert_list = cert_list)
        return_dict['form'] = form
        if not form.is_valid():
          return django.shortcuts.render_to_response("edit_https_mode.html", return_dict, context_instance = django.template.context.RequestContext(request))
        cd = form.cleaned_data
      if change_to == 'secure':
        pki_dir, err = common.get_pki_dir()
        if err:
          raise Exception(err)
        cert_loc = '%s/%s/%s.cert'%(pki_dir, cd['cert_name'], cd['cert_name'])
        if not os.path.exists(cert_loc):
          raise Exception('Error locating certificate')
        ret, err = nginx.generate_nginx_conf(True, cert_loc, cert_loc)
        if err:
          raise Exception(err)
      else:
        ret, err = nginx.generate_nginx_conf(False)
        if err:
          raise Exception(err)
      audit_str = "Changed the IntegralView access mode to '%s'"%change_to
      audit.audit("set_https_mode", audit_str, request.META["REMOTE_ADDR"])

      os.system('echo service nginx restart | at now + 1 minute')
 
      return django.http.HttpResponseRedirect('/view_https_mode?ack=set_to_%s'%change_to)

  except Exception, e:
    return_dict['base_template'] = "admin_base.html"
    return_dict["page_title"] = 'Set Integralview access mode'
    return_dict['tab'] = 'https_tab'
    return_dict["error"] = 'Error setting IntegralView access mode'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def reboot_or_shutdown(request):
  return_dict = {}
  audit_str = ""
  try:
    minutes_to_wait = 1
    return_dict['minutes_to_wait'] = minutes_to_wait
    if 'do' not in request.REQUEST:
      raise Exception('Unknown action. Please use the menus')
    else:
      do = request.REQUEST['do']
      return_dict['do'] = do
    if request.method == "GET":
      return django.shortcuts.render_to_response("reboot_or_shutdown.html", return_dict, context_instance=django.template.context.RequestContext(request))
    else:
      if 'conf' not in request.POST:
        raise Exception('Unknown action. Please use the menus')
      audit.audit('reboot_shutdown', 'System %s initiated'%do, request.META["REMOTE_ADDR"])
      if do == 'reboot':
        command.execute_with_rc('shutdown -r +%d'%minutes_to_wait)
      elif do == 'shutdown':
        command.execute_with_rc('shutdown -h +%d'%minutes_to_wait)
      return django.shortcuts.render_to_response("reboot_or_shutdown_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "system_base.html"
    return_dict["page_title"] = 'Reboot or Shutdown Failure'
    return_dict['tab'] = 'reboot_tab'
    return_dict["error"] = 'Error Rebooting'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))

def reload_manifest(request):
  return_dict = {}
  try:
    if request.method == "GET":
      from integralstor_common import manifest_status as iu
      mi, err = iu.generate_manifest_info()
      #print mi, err
      if err:
        raise Exception(err)
      if not mi:
        raise Exception('Could not load new configuration')
      return_dict["mi"] = mi[mi.keys()[0]] # Need the hostname here. 
      return django.shortcuts.render_to_response("reload_manifest.html", return_dict, context_instance=django.template.context.RequestContext(request))
    elif request.method == "POST":
      common_python_scripts_path, err = common.get_common_python_scripts_path()
      if err:
        raise Exception(err)
      ss_path, err = common.get_system_status_path()
      if err:
        raise Exception(err)
      #(ret,rc), err = command.execute_with_rc("python %s/generate_manifest.py %s"%(common_python_scripts_path, ss_path))
      ret, err = command.get_command_output("python %s/generate_manifest.py %s"%(common_python_scripts_path, ss_path))
      #print 'mani', ret, err
      if err:
        raise Exception(err)
      #(ret,rc), err = command.execute_with_rc("python %s/generate_status.py %s"%(common.get_python_scripts_path(), common.get_system_status_path()))
      ret, err = command.get_command_output("python %s/generate_status.py %s"%(common_python_scripts_path, ss_path))
      #print 'stat', ret, err
      if err:
        raise Exception(err)
      return django.http.HttpResponseRedirect("/view_system_info/")
  except Exception, e:
    return_dict['base_template'] = "system_base.html"
    return_dict["page_title"] = 'Reload system configuration'
    return_dict['tab'] = 'node_info_tab'
    return_dict["error"] = 'Error reloading system configuration'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

@login_required 
#@django.views.decorators.csrf.csrf_exempt
def flag_node(request):

  try:
    return_dict = {}
    if "node" not in request.GET:
      raise Exception("Error flagging node. No node specified")
  
    node_name = request.GET["node"]
    blink_time = 255
    use_salt, err = common.use_salt()
    if use_salt:
      import salt.client
      client = salt.client.LocalClient()
      ret = client.cmd(node_name,'cmd.run',['ipmitool chassis identify %s' %(blink_time)])
      print ret
      if ret[node_name] == 'Chassis identify interval: %s seconds'%(blink_time):
        return django.http.HttpResponse("Success")
      else:
        raise Exception("")
    else:
      out_list, err = command.get_command_output('service winbind status')
      if err:
        raise Exception(err)
      if 'Chassis identify interval: %s seconds'%(blink_time) in out_list[0]:
        return django.http.HttpResponse("Success")
      else:
        raise Exception("")
  except Exception, e:
    return django.http.HttpResponse("Error")


#this function takes a user argument checks if the user has administrator rights and then returns True.
#If he does not have the correct permissions, then then it returns a HTttpResponse stating No Permission to access this page.
#Takes user object as a parameter: request.user
# def is_superuser(user):
#   if user.is_superuser:
#     return True
#   else:
#     return False

def admin_login_required(view):

  def new_view(request, *args, **kwargs):
    if request.user.is_superuser:
      return view(request, *args, **kwargs)
    else:
      return django.http.HttpResponseRedirect('/login')

  return new_view
    
#The below function was commented. Uncommented it. Please review it again
@admin_login_required
def reset_to_factory_defaults(request):
  return_dict = {}
  try:
    if request.method == "GET":
      #Send a confirmation screen
      return django.shortcuts.render_to_response('reset_factory_defaults_conf.html', return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      iv_logging.info("Got a request to reset to factory defaults")
      #Post request so from conf screen
  
      #Reset the ntp config file
      try :
        shutil.copyfile("%s/factory_defaults/ntp.conf"%common.get_factory_defaults_path(), '%s/ntp.conf'%fractalio.common.get_ntp_conf_path())
        pass
      except Exception, e:
        return_dict["error"] = "Error reseting NTP configuration : %s"%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
      #Remove email settings
      try:
        mail.delete_email_settings()
      except Exception, e:
        #print str(e)
        return_dict["error"] = "Error reseting mail configuration : %s."%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
      try:
        audit.rotate_audit_trail()
      except Exception, e:
        #print str(e)
        return_dict["error"] = "Error rotating the audit trail : %s."%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
      #Remove all shares 
      try:
        cifs_common.delete_all_shares()
      except Exception, e:
        #print str(e)
        return_dict["error"] = "Error deleting shares : %s."%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
      try:
        cifs_common.delete_auth_settings()
      except Exception, e:
        return_dict["error"] = "Error deleting CIFS authentication settings : %s."%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
      try:
        request.user.set_password("admin");
        request.user.save()
      except Exception, e:
        return_dict["error"] = "Error resetting admin password: %s."%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
  
      #Reset the alerts file
      try :
        shutil.copyfile("%s/factory_defaults/alerts.log"%fractalio.common.get_factory_defaults_path(), '%s/alerts.log'%fractalio.common.get_alerts_path())
      except Exception, e:
        return_dict["error"] = "Error reseting alerts : %s."%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
      #Reset all batch jobs
      try :
        l = os.listdir("%s"%fractalio.common.get_batch_files_path())
        for fname in l:
          os.remove("%s/%s"%(fractalio.common.get_batch_files_path(), fname))
      except Exception, e:
        return_dict["error"] = "Error removing scheduled batch jobs : %s."%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
      try:
        iscsi.reset_global_target_conf()
        iscsi.delete_all_targets()
        iscsi.delete_all_initiators()
        iscsi.delete_all_auth_access_groups()
        iscsi.delete_all_auth_access_users()
      except Exception, e:
        return_dict["error"] = "Error resetting ISCSI configuration : %s."%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
      try:
        # Create commands to stop and delete volumes. Remove peers from cluster.
        vil = volume_info.get_volume_info_all()
        scl = system_info.load_system_config()
        d = gluster_commands.create_factory_defaults_reset_file(scl, vil)
        if not "error" in d:
          audit.audit("factory_defaults_reset_start", "Scheduled reset of the system to factory defaults.",  request.META["REMOTE_ADDR"])
          return django.http.HttpResponseRedirect('/show/batch_start_conf/%s'%d["file_name"])
        else:
          return_dict["error"] = "Error initiating a reset to system factory defaults : %s"%d["error"]
          return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
      except Exception, e:
        return_dict["error"] = "Error creating factory defaults reset batch file : %s."%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


'''

def remove_email_settings(request):

  response = django.http.HttpResponse()
  iv_logging.info("Email settings deleted")
  try:
    mail.delete_email_settings()
    response.write("Deleted email settings")
  except Exception, e:
    response.write("Error deleteing email settings : %s"%e)
  return response


'''
