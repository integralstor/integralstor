
import django
import django.template
from django.contrib import auth
from django.contrib.sessions.models import Session
import json

import integral_view
from integral_view.forms import admin_forms
from integral_view.utils import iv_logging

import fractalio
from fractalio import audit, mail 


def login(request):
  """ Used to login a user into the management utility"""

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
    return django.http.HttpResponseRedirect('/show/dashboard/')

  # For all other cases, return to login screen with return_dict 
  # appropriately populated
  return django.shortcuts.render_to_response('login_form.html', return_dict, context_instance = django.template.context.RequestContext(request))


def logout(request):
  """ Used to logout a user into the management utility"""
  iv_logging.info("User '%s' logged out"%request.user)
  # Clear the session if the user has been logged in anywhere else.
  sessions = Session.objects.all()
  for s in sessions:
   if s.get_decoded() and (s.get_decoded()['_auth_user_id'] == request.user.id or not s.get_decoded()):
      s.delete()
  django.contrib.auth.logout(request)
  return django.http.HttpResponseRedirect('/login/')

def change_admin_password(request):
  """ Used to change a user's password for the management utility"""

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

  
def configure_email_settings(request):

  return_dict = {}
  url = "edit_email_settings.html"
  if request.method=="GET":
    d = mail.load_email_settings()
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
      try:
        mail.save_email_settings(d)
      except Exception, e:
        iv_logging.debug("Exception when trying to save email settings : %s"%e)
        return django.http.HttpResponseRedirect("/show/email_settings?not_saved=1&err=%s"%str(e))

      ret = mail.send_mail(cd["email_server"], cd["email_server_port"], cd["username"], cd["pswd"], cd["tls"], cd["rcpt_list"], "Test email from FractalView", "This is a test email sent by the Fractal View system in order to confirm that your email settings are working correctly.")
      if ret:
        return django.http.HttpResponseRedirect("/show/email_settings?saved=1&err=%s"%ret)
      else:
        return django.http.HttpResponseRedirect("/show/email_settings?saved=1")
  return_dict["form"] = form
  return django.shortcuts.render_to_response(url, return_dict, context_instance = django.template.context.RequestContext(request))


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
