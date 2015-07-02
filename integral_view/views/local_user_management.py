
import django, django.template

import integral_view
from integral_view.forms import samba_shares_forms
from integral_view.samba import samba_settings, local_users

import salt.client

import integralstor_common
from integralstor_common import audit, networking

def view_local_users(request):

  return_dict = {}
  try:
    try:
      user_list = local_users.get_local_users()
    except Exception, e:
      return_dict["error"] = "Error retrieving local users - %s" %e
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
  
    return_dict["user_list"] = user_list
  
    if "action" in request.GET:
      if request.GET["action"] == "saved":
        conf = "Local user password successfully updated"
      elif request.GET["action"] == "created":
        conf = "Local user successfully created"
      elif request.GET["action"] == "deleted":
        conf = "Local user successfully deleted"
      elif request.GET["action"] == "changed_password":
        conf = "Successfully update password"
      return_dict["conf"] = conf
      if "warnings" in request.GET:
        return_dict["warnings"] = request.GET["warnings"]
  
    return django.shortcuts.render_to_response('view_local_users.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    if "Another transaction is in progress".lower() in s.lower():
      return_dict["error"] = "An underlying storage operation has locked a volume so we are unable to process this request. Please try after a couple of seconds"
    else:
      return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_local_user(request):
  return_dict = {}
  try:
    if request.method == "GET":
      #Return the form
      form = samba_shares_forms.LocalUserForm()
      return_dict["form"] = form
      return django.shortcuts.render_to_response("create_local_user.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      #Form submission so create
      return_dict = {}
      form = samba_shares_forms.LocalUserForm(request.POST)
      if form.is_valid():
        cd = form.cleaned_data
        try :
          ret = local_users.create_local_user(cd["userid"], cd["name"], cd["password"])
          audit_str = "Created a local user %s"%cd["userid"]
          audit.audit("create_local_user", audit_str, request.META["REMOTE_ADDR"])
          url = '/view_local_users?action=created'
          if ret:
            warnings = ','.join(ret)
            url = "%s&warnings=%s"%(url, warnings)
          return django.http.HttpResponseRedirect(url)
        except Exception, e:
          return_dict["error"] = "Error creating the local user - %s" %e
          return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
      else:
        return_dict["form"] = form
        return django.shortcuts.render_to_response("create_local_user.html", return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    if "Another transaction is in progress".lower() in s.lower():
      return_dict["error"] = "An underlying storage operation has locked a volume so we are unable to process this request. Please try after a couple of seconds"
    else:
      return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


  
def delete_local_user(request):

  return_dict = {}
  try:
    if "userid" not in request.REQUEST:
      return_dict["error"] = "Invalid request. No user name specified."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    
    if request.method == "GET":
      #Return the form
      return_dict["userid"] = request.GET["userid"]
      return django.shortcuts.render_to_response("delete_local_user_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      #Form submission so create
      return_dict = {}
      try :
        ret = local_users.delete_local_user(request.POST["userid"])
        audit_str = "Deleted a local user %s"%request.POST["userid"]
        audit.audit("delete_local_user", audit_str, request.META["REMOTE_ADDR"])
        url = '/view_local_users?action=deleted'
        if ret:
          warnings = ','.join(ret)
          url = "%s&warnings=%s"%(url, warnings)
        return django.http.HttpResponseRedirect(url)
      except Exception, e:
        return_dict["error"] = "Error deleting the local user - %s" %e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    if "Another transaction is in progress".lower() in s.lower():
      return_dict["error"] = "An underlying storage operation has locked a volume so we are unable to process this request. Please try after a couple of seconds"
    else:
      return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def change_local_user_password(request):

  return_dict = {}
  try:
    if request.method == "GET":
      #Return the form
      if "userid" not in request.GET:
        return_dict["error"] = "Invalid request. No user name specified."
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
      d = {}
      d["userid"] = request.GET["userid"]
      form = samba_shares_forms.PasswordChangeForm(initial=d)
      return_dict["form"] = form
      return django.shortcuts.render_to_response("change_local_user_password.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      #Form submission so create
      return_dict = {}
      form = samba_shares_forms.PasswordChangeForm(request.POST)
      if form.is_valid():
        cd = form.cleaned_data
        try :
          local_users.change_password(cd["userid"], cd["password"])
        except Exception, e:
          return_dict["error"] = "Error creating the local user - %s" %e
          return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
  
        audit_str = "Changed password for local user %s"%cd["userid"]
        audit.audit("change_local_user_password", audit_str, request.META["REMOTE_ADDR"])
        return django.http.HttpResponseRedirect('/view_local_users?action=changed_password')
      else:
        return_dict["form"] = form
        return django.shortcuts.render_to_response("change_local_user_password.html", return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    if "Another transaction is in progress".lower() in s.lower():
      return_dict["error"] = "An underlying storage operation has locked a volume so we are unable to process this request. Please try after a couple of seconds"
    else:
      return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

