
import django
import django.template
from django.contrib import auth
from django.contrib.sessions.models import Session
import json, os, shutil, re

import integral_view
from integral_view.forms import admin_forms
from integral_view.utils import iv_logging

import integralstor_common
from integralstor_common import audit, mail, common


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


def _get_nginx_access_mode():
  mode = {}
  try:
    with open('/etc/nginx/sites-enabled/integral_view_nginx.conf', 'r') as f:
      lines = f.readlines()
      for line in lines:
        #print line
        ret = re.search('[\s]*[lL]isten[\s]*([0-9]+)', line.lower())
        if ret:
          grps = ret.groups()
          if grps:
            mode['port'] = int(grps[0])
        ret = re.search('[\s]*ssl_certificate[\s]+([\S]*)', line)
        if ret:
          grps = ret.groups()
          if grps:
            mode['certificate'] = grps[0]
        ret = re.search('[\s]*ssl_certificate_key[\s]*([\S]*)', line)
        if ret:
          grps = ret.groups()
          if grps:
            mode['key'] = grps[0]
  except Exception, e:
    return None, 'Error getting web server access mode : %s'%str(e)
  else:
    return mode, None

def _generate_nginx_conf(ssl=False, ssl_cert_file = None, ssl_key_file = None):
  try:
    platform_root, err = common.get_platform_root()
    if err:
      raise Exception(err)
    shutil.copyfile('/etc/nginx/sites-enabled/integral_view_nginx.conf', '/tmp/integral_view_nginx.conf')
    with open('/etc/nginx/sites-enabled/integral_view_nginx.conf', 'w') as f:
      f.write('upstream django {\n')
      f.write(' server unix:////opt/integralstor/integralstor_unicell/integral_view/integral_view.sock;\n')
      f.write('}\n')
      f.write('\n')
      f.write('server {\n')
      if ssl:
        f.write('  listen      443 ssl;\n')
        f.write('  ssl_certificate %s;\n'%ssl_cert_file)
        f.write('  ssl_certificate_key %s;\n'%ssl_key_file)
      else:
        f.write('  listen      80;\n')

      f.write('  charset     utf-8;\n')
      f.write('  client_max_body_size 75M;\n')
      f.write('  location /static {\n')
      f.write('    alias %s/integral_view/static;\n'%platform_root)
      f.write('  }\n')
      f.write('\n')
      f.write('  location / {\n')
      f.write('    uwsgi_pass  django;\n')
      f.write('    include     %s/integral_view/uwsgi_params;\n'%platform_root)
      f.write('  }\n')
      f.write('}\n')
  except Exception, e:
    if os.path.exists('/tmp/integral_view_nginx.conf'):
      shutil.copyfile('/tmp/integral_view_nginx.conf', '/etc/nginx/sites-enabled/integral_view_nginx.conf')
    return False, 'Error generating HTTPS configuration : %s'%str(e)
  else:
    return True, None

def main():
  #print _generate_nginx_conf(False)
  #print _get_nginx_access_mode()
  #print _generate_nginx_conf(True, '/opt/integralstor/pki/blah/blah.cert', '/opt/integralstor/pki/blah/blah.cert')
  print _get_nginx_access_mode()

if __name__ == '__main__':
  main()
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
