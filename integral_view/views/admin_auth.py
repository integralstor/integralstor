
import django
import django.template
from django.contrib import auth
from django.contrib.sessions.models import Session
import json, os, shutil, re, subprocess

import integral_view
from integral_view.forms import admin_forms, pki_forms
from integral_view.utils import iv_logging

from integralstor_common import audit, mail, common, certificates, services_management, command, nginx


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
          if production:
            # Clear the session if the user has been logged in anywhere else.
            sessions = Session.objects.all()
            for s in sessions:
              if s.get_decoded() and (s.get_decoded()['_auth_user_id'] == user.id):
                s.delete()
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
      return django.http.HttpResponseRedirect('/dashboard/disks')

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
              return_dict['success'] = True
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
        if d["tls"]:
          d["tls"] = True
        else:
          d["tls"] = False
        if d["email_alerts"]:
          d["email_alerts"] = True
        else:
          d["email_alerts"] = False
        form = admin_forms.ConfigureEmailForm(initial = {'email_server':d["server"], 'email_server_port':d["port"], 'tls':d["tls"], 'username':d["username"], 'email_alerts':d["email_alerts"], 'rcpt_list':d["rcpt_list"]})
    else:
      form = admin_forms.ConfigureEmailForm(request.POST)
      if form.is_valid():
        cd = form.cleaned_data
        d = {}
        if "email_alerts" in cd:
          d["email_alerts"] = cd["email_alerts"]
        else:
          d["email_alerts"] = False
        d["server"] = cd["email_server"]
        d["port"] = cd["email_server_port"]
        d["username"] = cd["username"]
        d["pswd"] = cd["pswd"]
        d["rcpt_list"] = cd["rcpt_list"]
        if "tls" in cd:
          d["tls"] = cd["tls"]
        else:
          d["tls"] = False
        #print "Saving : "
        #print d
        ret, err = mail.save_email_settings(d)
        if err:
          raise Exception(err)

        ret, err = mail.send_mail(cd["email_server"], cd["email_server_port"], cd["username"], cd["pswd"], cd["tls"], cd["rcpt_list"], "Test email from IntegralStor", "This is a test email sent by the IntegralStor system in order to confirm that your email settings are working correctly.")
        if err:
          raise Exception(err)
        if ret:
          return django.http.HttpResponseRedirect("/show/email_settings?saved=1&err=%s"%ret)
        else:
          return django.http.HttpResponseRedirect("/show/email_settings?saved=1")
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
  mode = {}
  try:
    return_dict = {}
    mode, err = nginx.get_nginx_access_mode()
    if err:
      raise Exception(err)
  
    conf = None
    if "action" in request.GET:
      if request.GET["action"] == "set_to_secure":
        conf = "The IntegralView access mode has been successfully set to secure(HTTPS). The server has been scheduled to restart. Please change your browser to access IntegralView using https://<integralview_ip_address>"
      elif request.GET["action"] == "set_to_nonsecure":
        conf = "The IntegralView access mode has been successfully set to non-secure(HTTP). The server has been scheduled to restart. Please change your browser to access IntegralView using http://<integralview_ip_address>"
      if conf:
        return_dict["conf"] = conf
    return_dict['port'] = mode['port']
    return django.shortcuts.render_to_response('view_https_mode.html', return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "system_base.html"
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
      #Return the conf page
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
 
      return django.http.HttpResponseRedirect('/view_https_mode?action=set_to_%s'%change_to)
  except Exception, e:
    return_dict['base_template'] = "system_base.html"
    return_dict["page_title"] = 'Set Integralview access mode'
    return_dict['tab'] = 'https_tab'
    return_dict["error"] = 'Error setting IntegralView access mode'
    return_dict["error_details"] = str(e)
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
