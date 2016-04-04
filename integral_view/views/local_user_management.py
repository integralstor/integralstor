
import django, django.template

import integral_view
from integral_view.forms import local_user_forms

from integralstor_common import audit
from integralstor_unicell import local_users

def view_local_users(request):

  return_dict = {}
  try:
    user_list, err = local_users.get_local_users()
    if err:
      raise Exception(err)
  
    return_dict["user_list"] = user_list
  
    if "ack" in request.GET:
      if request.GET["ack"] == "saved":
        return_dict['ack_message'] = "Local user password successfully updated"
      elif request.GET["ack"] == "created":
        return_dict['ack_message'] = "Local user successfully created"
      elif request.GET["ack"] == "deleted":
        return_dict['ack_message'] = "Local user successfully deleted"
      elif request.GET["ack"] == "changed_password":
        return_dict['ack_message'] = "Successfully update password"
  
    return django.shortcuts.render_to_response('view_local_users.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = 'users-groups_base.html'
    return_dict["page_title"] = 'Local users'
    return_dict['tab'] = 'view_local_users_tab'
    return_dict["error"] = 'Error loading local users list'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_local_groups(request):

  return_dict = {}
  try:
    group_list, err = local_users.get_local_groups()
    if err:
      raise Exception(err)
  
    return_dict["group_list"] = group_list
  
    if "ack" in request.GET:
      if request.GET["ack"] == "created":
        return_dict['ack_message'] = "Local group successfully created"
      elif request.GET["ack"] == "deleted":
        return_dict['ack_message'] = "Local group successfully deleted"
  
    return django.shortcuts.render_to_response('view_local_groups.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = 'users-groups_base.html'
    return_dict["page_title"] = 'Local groups'
    return_dict['tab'] = 'view_local_groups_tab'
    return_dict["error"] = 'Error loading local groups list'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_local_user(request):

  return_dict = {}
  try:
    if 'searchby' not in request.GET:
      raise Exception("Malformed request. Please use the menus.")

    if request.GET['searchby'] == 'username':
      if 'username' not in request.GET:
        raise Exception("Malformed request. Please use the menus.")
      ud,err = local_users.get_local_user(request.GET['username'])
    elif request.GET['searchby'] == 'uid':
      if 'uid' not in request.GET:
        raise Exception("Malformed request. Please use the menus.")
      ud,err = local_users.get_local_user(request.GET['username'], False)

    if err:
      raise Exception(err)

    if not ud:
      raise Exception("Specified user not found. Please use the menus.")
      
    return_dict["user"] = ud
  
    if "ack" in request.GET:
      if request.GET["ack"] == "gid_changed":
        return_dict['ack_message'] = "Local user's group successfully updated"
      elif request.GET["ack"] == "changed_password":
        return_dict['ack_message'] = "Successfully update password"
  
    return django.shortcuts.render_to_response('view_local_user.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = 'users-groups_base.html'
    return_dict["page_title"] = 'Local user details'
    return_dict['tab'] = 'view_local_users_tab'
    return_dict["error"] = 'Error loading local user details'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_local_group(request):

  return_dict = {}
  try:
    if 'searchby' not in request.GET:
      raise Exception("Malformed request. Please use the menus.")
    if request.GET['searchby'] == 'grpname':
      if 'grpname' not in request.GET:
        raise Exception("Malformed request. Please use the menus.")
      gd,err = local_users.get_local_group(request.GET['grpname'])
    elif request.GET['searchby'] == 'gid':
      if 'gid' not in request.GET:
        raise Exception("Malformed request. Please use the menus.")
      gd,err = local_users.get_local_group(request.GET['grpname'], False)

    if err:
      raise Exception(err)

    if not gd:
      raise Exception("Specified group not found. Please use the menus.")
      
    return_dict["group"] = gd
  
    if "ack" in request.GET:
      if request.GET["ack"] == "gid_changed":
        return_dict['ack_message'] = "Local user's group successfully updated"
      elif request.GET["ack"] == "changed_password":
        return_dict['ack_message'] = "Successfully update password"
  
    return django.shortcuts.render_to_response('view_local_group.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = 'users-groups_base.html'
    return_dict["page_title"] = 'Local group details'
    return_dict['tab'] = 'view_local_groups_tab'
    return_dict["error"] = 'Error loading local group details '
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def edit_local_user_gid(request):

  return_dict = {}
  try:
    group_list,err = local_users.get_local_groups()
    if err:
      raise Exception(err)
    if 'username' not in request.REQUEST:
      raise Exception("Unknown user specified")

    username = request.REQUEST["username"]
    ud,err = local_users.get_local_user(username)
    if err:
      raise Exception(err)
    if not ud:
      raise Exception("Specified user information not found")
  
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
            raise Exception(err)
          else:
            raise Exception("Error saving user information")
  
        audit_str = "Modified local user's primary group %s"%cd["username"]
        audit.audit("modify_local_user_gid", audit_str, request.META["REMOTE_ADDR"])
  
        return django.http.HttpResponseRedirect('/view_local_user?username=%s&searchby=username&ack=gid_changed'%cd["username"])
  
      else:
        #Invalid form
        return django.shortcuts.render_to_response('edit_local_user_gid.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = 'users-groups_base.html'
    return_dict["page_title"] = "Modify local user's primary group"
    return_dict['tab'] = 'view_local_users_tab'
    return_dict["error"] = 'Error modifying local users primary group'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def edit_local_user_group_membership(request):

  return_dict = {}
  try:
    t_group_list,err = local_users.get_local_groups()
    if err:
      raise Exception(err)
    if 'username' not in request.REQUEST:
      raise Exception("Unknown user specified")

    username = request.REQUEST["username"]
    ud,err = local_users.get_local_user(username)
    if err:
      raise Exception(err)
    if not ud:
      raise Exception("Specified user information not found")
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
            raise Exception(err)
          else:
            raise Exception("Error saving user's group membership information")
  
        audit_str = "Modified local user group membership information %s"%cd["username"]
        audit.audit("modify_local_user_grp_membership", audit_str, request.META["REMOTE_ADDR"])
  
        return django.http.HttpResponseRedirect('/view_local_user?username=%s&searchby=username&ack=groups_changed'%cd["username"])
  
      else:
        #Invalid form
        return django.shortcuts.render_to_response('edit_local_user_group_membership.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = 'users-groups_base.html'
    return_dict["page_title"] = 'Local users additional group membership'
    return_dict['tab'] = 'view_local_users_tab'
    return_dict["error"] = 'Error modifying local users additional group membership'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_local_user(request):
  return_dict = {}
  try:
    group_list,err = local_users.get_local_groups()
    if err:
      raise Exception(err)
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
            raise Exception(err)
          else:
            raise Exception("Error creating the local user.")
                
        audit_str = "Created a local user %s"%cd["username"]
        audit.audit("create_local_user", audit_str, request.META["REMOTE_ADDR"])
        url = '/view_local_users?ack=created'
        return django.http.HttpResponseRedirect(url)
      else:
        return_dict["form"] = form
        return django.shortcuts.render_to_response("create_local_user.html", return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = 'users-groups_base.html'
    return_dict["page_title"] = 'Create a local users'
    return_dict['tab'] = 'view_local_users_tab'
    return_dict["error"] = 'Error creating a local user'
    return_dict["error_details"] = str(e)
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
      #print '1'
      form = local_user_forms.LocalGroupForm(request.POST)
      if form.is_valid():
        #print '2'
        cd = form.cleaned_data
        ret, err = local_users.create_local_group(cd["grpname"])
        #print '3'
        if not ret:
          if err:
            raise Exception(err)
          else:
            raise Exception("Error creating the local group.")
        audit_str = "Created a local group %s"%cd["grpname"]
        audit.audit("create_local_group", audit_str, request.META["REMOTE_ADDR"])
        url = '/view_local_groups?ack=created'
        return django.http.HttpResponseRedirect(url)
      else:
        return_dict["form"] = form
        return django.shortcuts.render_to_response("create_local_group.html", return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = 'users-groups_base.html'
    return_dict["page_title"] = 'Create a local user group'
    return_dict['tab'] = 'view_local_groups_tab'
    return_dict["error"] = 'Error create a local user group'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
  
def delete_local_group(request):
  return_dict = {}
  try:
    if "grpname" not in request.REQUEST:
      raise Exception("Invalid request. No group name specified.")
    
    gd, err = local_users.get_local_group(request.REQUEST['grpname'])
    if err or (not gd):
      if err:
        raise Exception(err)
      else:
        raise Exception("Could not retrieve group information")

    if gd['members']:
      raise Exception("Cannot delete this group as it has the following members : %s"%(','.join(gd['members'])))

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
      url = '/view_local_groups?ack=deleted'
      return django.http.HttpResponseRedirect(url)
  except Exception, e:
    return_dict['base_template'] = 'users-groups_base.html'
    return_dict["page_title"] = 'Delete a local user group'
    return_dict['tab'] = 'view_local_groups_tab'
    return_dict["error"] = 'Error deleting a local user group'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def delete_local_user(request):

  return_dict = {}
  try:
    if "username" not in request.REQUEST:
      raise Exception("Invalid request. No user name specified.")
    
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
          raise Exception(err)
        else:
          raise Exception('Error deleting local user')
      audit_str = "Deleted a local user %s"%request.POST["username"]
      audit.audit("delete_local_user", audit_str, request.META["REMOTE_ADDR"])
      url = '/view_local_users?ack=deleted'
      return django.http.HttpResponseRedirect(url)
  except Exception, e:
    return_dict['base_template'] = 'users-groups_base.html'
    return_dict["page_title"] = 'Delete a local user'
    return_dict['tab'] = 'view_local_users_tab'
    return_dict["error"] = 'Error deleting a local user'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def change_local_user_password(request):

  return_dict = {}
  try:
    if request.method == "GET":
      #Return the form
      if "username" not in request.GET:
        raise Exception("Invalid request. No user name specified.")
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
            raise Exception(err)
          else:
            raise Exception("Error changing the local user password")
  
        audit_str = "Changed password for local user %s"%cd["username"]
        audit.audit("change_local_user_password", audit_str, request.META["REMOTE_ADDR"])
        return django.http.HttpResponseRedirect('/view_local_users?ack=changed_password')
      else:
        return_dict["form"] = form
        return django.shortcuts.render_to_response("change_local_user_password.html", return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = 'users-groups_base.html'
    return_dict["page_title"] = "Modify local user's password"
    return_dict['tab'] = 'view_local_users_tab'
    return_dict["error"] = "Error modifying local user's password"
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

