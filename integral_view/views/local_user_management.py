
import django, django.template

import integral_view
from integral_view.forms import local_user_forms
from integral_view.samba import samba_settings, local_users

import integralstor_common
from integralstor_common import audit, networking

def view_local_users(request):

  return_dict = {}
  try:
    user_list, err = local_users.get_local_users()
    if err:
      raise Exception(err)
  
    return_dict["user_list"] = user_list
  
    if "action" in request.GET:
      conf = ''
      if request.GET["action"] == "saved":
        conf = "Local user password successfully updated"
      elif request.GET["action"] == "created":
        conf = "Local user successfully created"
      elif request.GET["action"] == "deleted":
        conf = "Local user successfully deleted"
      elif request.GET["action"] == "changed_password":
        conf = "Successfully update password"
      return_dict["conf"] = conf
  
    return django.shortcuts.render_to_response('view_local_users.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_local_groups(request):

  return_dict = {}
  try:
    group_list, err = local_users.get_local_groups()
    if err:
      raise Exception(err)
  
    return_dict["group_list"] = group_list
  
    if "action" in request.GET:
      conf = ''
      if request.GET["action"] == "created":
        conf = "Local group successfully created"
      elif request.GET["action"] == "deleted":
        conf = "Local group successfully deleted"
      return_dict["conf"] = conf
  
    return django.shortcuts.render_to_response('view_local_groups.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_local_user(request):

  return_dict = {}
  try:
    if 'searchby' not in request.GET:
      return_dict["error"] = "Malformed request. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    if request.GET['searchby'] == 'username':
      if 'username' not in request.GET:
        return_dict["error"] = "Malformed request. Please use the menus."
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
      ud,err = local_users.get_local_user(request.GET['username'])
    elif request.GET['searchby'] == 'uid':
      if 'uid' not in request.GET:
        return_dict["error"] = "Malformed request. Please use the menus."
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
      ud,err = local_users.get_local_user(request.GET['username'], False)

    if err:
      raise Exception(err)

    if not ud:
      return_dict["error"] = "Specified user not found. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
      
    return_dict["user"] = ud
  
    if "action" in request.GET:
      conf = ''
      if request.GET["action"] == "gid_changed":
        conf = "Local user's group successfully updated"
      elif request.GET["action"] == "changed_password":
        conf = "Successfully update password"
      return_dict["conf"] = conf
  
    return django.shortcuts.render_to_response('view_local_user.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_local_group(request):

  return_dict = {}
  try:
    if 'searchby' not in request.GET:
      return_dict["error"] = "Malformed request. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    if request.GET['searchby'] == 'grpname':
      if 'grpname' not in request.GET:
        return_dict["error"] = "Malformed request. Please use the menus."
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
      gd,err = local_users.get_local_group(request.GET['grpname'])
    elif request.GET['searchby'] == 'gid':
      if 'gid' not in request.GET:
        return_dict["error"] = "Malformed request. Please use the menus."
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
      gd,err = local_users.get_local_group(request.GET['grpname'], False)

    if err:
      raise Exception(err)

    if not gd:
      return_dict["error"] = "Specified group not found. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
      
    return_dict["group"] = gd
  
    if "action" in request.GET:
      conf = ''
      '''
      if request.GET["action"] == "gid_changed":
        conf = "Local user's group successfully updated"
      elif request.GET["action"] == "changed_password":
        conf = "Successfully update password"
      return_dict["conf"] = conf
      '''
  
    return django.shortcuts.render_to_response('view_local_group.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def edit_local_user_gid(request):

  return_dict = {}
  try:
    group_list,err = local_users.get_local_groups()
    if err:
      return_dict["error"] = "Error loading group list information - %s" %err
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    if 'username' not in request.REQUEST:
      return_dict["error"] = "Unknown user specified"
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    username = request.REQUEST["username"]
    ud,err = local_users.get_local_user(username)
    if err:
      return_dict["error"] = "Error loading user information - %s" %err
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    if not ud:
      return_dict["error"] = "Specified user information not found"
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
  
    if request.method == "GET":
      # Shd be an edit request
  
      # Set initial form values
      initial = {}
      initial['username'] = ud['username']
      initial['gid'] = ud['gid']
  
      form = local_user_forms.EditLocalUserGidForm(initial = initial, group_list = group_list)
  
      return_dict["form"] = form
      return django.shortcuts.render_to_response('edit_local_user_gid.html', return_dict, context_instance=django.template.context.RequestContext(request))
  
    else:
  
      # Shd be an save request
      form = local_user_forms.EditLocalUserGidForm(request.POST, group_list = group_list)
      return_dict["form"] = form
      if form.is_valid():
        cd = form.cleaned_data
        ret, err = local_users.set_local_user_gid(cd)
        if not ret:
          if err:
            return_dict["error"] = "Error saving user information - %s" %err
          else:
            return_dict["error"] = "Error saving user information"
          return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
  
        audit_str = "Modified local user's primary group %s"%cd["username"]
        audit.audit("modify_local_user_gid", audit_str, request.META["REMOTE_ADDR"])
  
        return django.http.HttpResponseRedirect('/view_local_user?username=%s&searchby=username&action=gid_changed'%cd["username"])
  
      else:
        #Invalid form
        return django.shortcuts.render_to_response('edit_local_user_gid.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def edit_local_user_group_membership(request):

  return_dict = {}
  try:
    t_group_list,err = local_users.get_local_groups()
    if err:
      return_dict["error"] = "Error loading group list information - %s" %err
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    if 'username' not in request.REQUEST:
      return_dict["error"] = "Unknown user specified"
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    username = request.REQUEST["username"]
    ud,err = local_users.get_local_user(username)
    if err:
      return_dict["error"] = "Error loading user information - %s" %err
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    if not ud:
      return_dict["error"] = "Specified user information not found"
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    group_list = []
    if t_group_list:
      for g in t_group_list:
        if g['grpname'] == ud['grpname']:
          continue
        else:
          group_list.append(g)
  
    if request.method == "GET":
      # Shd be an edit request
  
      # Set initial form values
      initial = {}
      initial['username'] = ud['username']
      initial['groups'] = ud['other_groups']
  
      form = local_user_forms.EditLocalUserGroupMembershipForm(initial = initial, group_list = group_list)
  
      return_dict["form"] = form
      return django.shortcuts.render_to_response('edit_local_user_group_membership.html', return_dict, context_instance=django.template.context.RequestContext(request))
  
    else:
  
      # Shd be an save request
      form = local_user_forms.EditLocalUserGroupMembershipForm(request.POST, group_list = group_list)
      return_dict["form"] = form
      if form.is_valid():
        cd = form.cleaned_data
        ret, err = local_users.set_local_user_group_membership(cd)
        if not ret:
          if err:
            return_dict["error"] = "Error saving user's group membership information - %s" %err
          else:
            return_dict["error"] = "Error saving user's group membership information"
          return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
  
        audit_str = "Modified local user group membership information %s"%cd["username"]
        audit.audit("modify_local_user_grp_membership", audit_str, request.META["REMOTE_ADDR"])
  
        return django.http.HttpResponseRedirect('/view_local_user?username=%s&searchby=username&action=groups_changed'%cd["username"])
  
      else:
        #Invalid form
        return django.shortcuts.render_to_response('edit_local_user_group_membership.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_local_user(request):
  return_dict = {}
  try:
    group_list,err = local_users.get_local_groups()
    if err:
      return_dict["error"] = "Error loading group list information - %s" %err
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    if request.method == "GET":
      #Return the form
      form = local_user_forms.LocalUserForm(group_list = group_list)
      return_dict["form"] = form
      return django.shortcuts.render_to_response("create_local_user.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      #Form submission so create
      return_dict = {}
      form = local_user_forms.LocalUserForm(request.POST, group_list = group_list)
      if form.is_valid():
        cd = form.cleaned_data
        ret, err = local_users.create_local_user(cd["username"], cd["name"], cd["password"], cd['gid'])
        if not ret:
          if err:
            return_dict["error"] = "Error creating the local user - %s" %err
          else:
            return_dict["error"] = "Error creating the local user."
          return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
        audit_str = "Created a local user %s"%cd["username"]
        audit.audit("create_local_user", audit_str, request.META["REMOTE_ADDR"])
        url = '/view_local_users?action=created'
        return django.http.HttpResponseRedirect(url)
      else:
        return_dict["form"] = form
        return django.shortcuts.render_to_response("create_local_user.html", return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_local_group(request):
  return_dict = {}
  try:
    if request.method == "GET":
      #Return the form
      form = local_user_forms.LocalGroupForm()
      return_dict["form"] = form
      return django.shortcuts.render_to_response("create_local_group.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      #Form submission so create
      return_dict = {}
      print '1'
      form = local_user_forms.LocalGroupForm(request.POST)
      if form.is_valid():
        print '2'
        cd = form.cleaned_data
        ret, err = local_users.create_local_group(cd["grpname"])
        print '3'
        if not ret:
          if err:
            return_dict["error"] = "Error creating the local group - %s" %err
          else:
            return_dict["error"] = "Error creating the local group."
          return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
        audit_str = "Created a local group %s"%cd["grpname"]
        audit.audit("create_local_group", audit_str, request.META["REMOTE_ADDR"])
        url = '/view_local_groups?action=created'
        return django.http.HttpResponseRedirect(url)
      else:
        return_dict["form"] = form
        return django.shortcuts.render_to_response("create_local_group.html", return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
  
def delete_local_group(request):
  return_dict = {}
  try:
    if "grpname" not in request.REQUEST:
      return_dict["error"] = "Invalid request. No group name specified."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    
    gd, err = local_users.get_local_group(request.REQUEST['grpname'])
    if err or (not gd):
      if err:
        return_dict["error"] = "Error retrieving group information : %s"%err
      else:
        return_dict["error"] = "Could not retrieve group information"
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

    if gd['members']:
      return_dict["error"] = "Cannot delete this group as it has the following members : %s"%(','.join(gd['members']))
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

    if request.method == "GET":
      #Return the form
      return_dict["grpname"] = request.GET["grpname"]
      return django.shortcuts.render_to_response("delete_local_group_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      #Form submission so create
      return_dict = {}
      ret, err = local_users.delete_local_group(request.POST["grpname"])
      if not ret:
        if err:
          raise Exception('Error deleting group : %s'%err)
        else:
          raise Exception('Error deleting group')
      audit_str = "Deleted a local group %s"%request.POST["grpname"]
      audit.audit("delete_local_group", audit_str, request.META["REMOTE_ADDR"])
      url = '/view_local_groups?action=deleted'
      return django.http.HttpResponseRedirect(url)
  except Exception, e:
    return_dict["error"] = "An error occurred when processing your request : %s"%str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def delete_local_user(request):

  return_dict = {}
  try:
    if "username" not in request.REQUEST:
      return_dict["error"] = "Invalid request. No user name specified."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    
    if request.method == "GET":
      #Return the form
      return_dict["username"] = request.GET["username"]
      return django.shortcuts.render_to_response("delete_local_user_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      #Form submission so create
      return_dict = {}
      ret, err = local_users.delete_local_user(request.POST["username"])
      if not ret:
        if err:
          raise Exception('Error deleting user : %s'%err)
        else:
          raise Exception('Error deleting user')
      audit_str = "Deleted a local user %s"%request.POST["username"]
      audit.audit("delete_local_user", audit_str, request.META["REMOTE_ADDR"])
      url = '/view_local_users?action=deleted'
      return django.http.HttpResponseRedirect(url)
  except Exception, e:
    return_dict["error"] = "An error occurred when processing your request : %s"%str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def change_local_user_password(request):

  return_dict = {}
  try:
    if request.method == "GET":
      #Return the form
      if "username" not in request.GET:
        return_dict["error"] = "Invalid request. No user name specified."
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
      d = {}
      d["username"] = request.GET["username"]
      form = local_user_forms.PasswordChangeForm(initial=d)
      return_dict["form"] = form
      return django.shortcuts.render_to_response("change_local_user_password.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      #Form submission so create
      return_dict = {}
      form = local_user_forms.PasswordChangeForm(request.POST)
      if form.is_valid():
        cd = form.cleaned_data
        rc, err = local_users.change_password(cd["username"], cd["password"])
        if not rc:
          if err:
            return_dict["error"] = "Error changing the local user password- %s" %err
          else:
            return_dict["error"] = "Error changing the local user password"
          return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
  
        audit_str = "Changed password for local user %s"%cd["username"]
        audit.audit("change_local_user_password", audit_str, request.META["REMOTE_ADDR"])
        return django.http.HttpResponseRedirect('/view_local_users?action=changed_password')
      else:
        return_dict["form"] = form
        return django.shortcuts.render_to_response("change_local_user_password.html", return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

