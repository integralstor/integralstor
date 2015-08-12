
import integralstor_common
from integralstor_common import audit, zfs
from integralstor_unicell import iscsi_stgt
from integral_view.forms import iscsi_stgt_forms

import django, django.template

def view_targets(request):

  return_dict = {}
  try:
    target_list, err = iscsi_stgt.get_targets()
    if err:
      raise Exception(err)
  
    return_dict["target_list"] = target_list
  
    if "action" in request.GET:
      conf = ''
      if request.GET["action"] == "created":
        conf = "ISCSI target successfully created"
      elif request.GET["action"] == "target_deleted":
        conf = "ISCSI target successfully created"
      elif request.GET["action"] == "lun_created":
        conf = "ISCSI LUN successfully created"
      elif request.GET["action"] == "added_acl":
        conf = "ISCSI target ACL successfully added"
      elif request.GET["action"] == "removed_acl":
        conf = "ISCSI target ACL successfully removed"
      elif request.GET["action"] == "lun_deleted":
        conf = "ISCSI LUN successfully deleted"
      elif request.GET["action"] == "deleted":
        conf = "ISCSI target successfully deleted"
      elif request.GET["action"] == "added_initiator_authentication":
        conf = "ISCSI initiator authentication successfully added"
      elif request.GET["action"] == "added_target_authentication":
        conf = "ISCSI target authentication successfully added"
      elif request.GET["action"] == "removed_initiator_authentication":
        conf = "ISCSI initiator authentication successfully removed"
      elif request.GET["action"] == "removed_target_authentication":
        conf = "ISCSI target authentication successfully removed"
      return_dict["conf"] = conf
  
    return django.shortcuts.render_to_response('view_iscsi_targets.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
  
def view_target(request):

  return_dict = {}
  try:
    if 'name' not in request.GET:
      return_dict["error"] = "Malformed request. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

    target, err = iscsi_stgt.get_target(request.GET['name'])
    if err:
      raise Exception(err)

    if not target:
      return_dict["error"] = "Specified target not found. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
      
    return_dict["target"] = target
  
    '''
    if "action" in request.GET:
      conf = ''
      if request.GET["action"] == "gid_changed":
        conf = "Local user's group successfully updated"
      elif request.GET["action"] == "changed_password":
        conf = "Successfully update password"
      return_dict["conf"] = conf
    '''
  
    return django.shortcuts.render_to_response('view_iscsi_target.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_iscsi_target(request):
  return_dict = {}
  try:
    if request.method == "GET":
      #Return the form
      form = iscsi_stgt_forms.IscsiTargetForm()
      return_dict["form"] = form
      return django.shortcuts.render_to_response("create_iscsi_target.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      #Form submission so create
      return_dict = {}
      form = iscsi_stgt_forms.IscsiTargetForm(request.POST)
      if form.is_valid():
        cd = form.cleaned_data
        ret, err = iscsi_stgt.create_target(cd["name"])
        if not ret:
          if err:
            return_dict["error"] = "Error creating the ISCSI target - %s" %err
          else:
            return_dict["error"] = "Error creating the ISCSI target."
          return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
        audit_str = "Created an ISCSI target %s"%cd["name"]
        audit.audit("create_iscsi_target", audit_str, request.META["REMOTE_ADDR"])
        url = '/view_iscsi_targets?action=created'
        return django.http.HttpResponseRedirect(url)
      else:
        return_dict["form"] = form
        return django.shortcuts.render_to_response("create_iscsi_target.html", return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def delete_iscsi_target(request):
  return_dict = {}
  try:
    if 'target_name' not in request.REQUEST:
      return_dict["error"] = "Malformed request. No target specified. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

    target_name = request.REQUEST['target_name']

    if request.method == "GET":
      return_dict["target_name"] = target_name
      return django.shortcuts.render_to_response("delete_iscsi_target_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      ret, err = iscsi_stgt.delete_target(target_name)
      if not ret:
        if err:
          return_dict["error"] = "Error deleting the ISCSI target - %s" %err
        else:
          return_dict["error"] = "Error deleting the ISCSI target."
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
      audit_str = "Deleted ISCSI target %s"%target_name
      url = '/view_iscsi_targets?action=target_deleted'
      audit.audit("delete_iscsi_target", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect(url)
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_iscsi_lun(request):

  return_dict = {}
  if 'target_name' not in request.REQUEST:
    return_dict["error"] = "Malformed request. No target specified. Please use the menus."
    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

  target_name = request.REQUEST['target_name']

  try:
    zvols, err = zfs.get_all_zvols()
    if err:
      raise Exception(err)
    if not zvols:
      return_dict["error"] = "There are no block device volumes created. Please create one first before adding a LUN."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    if request.method == "GET":
      #Return the form
      initial = {}
      initial['target_name'] = target_name
      form = iscsi_stgt_forms.IscsiLunForm(initial = initial, zvols = zvols)
      return_dict["form"] = form
      return django.shortcuts.render_to_response("create_iscsi_lun.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      #Form submission so create
      return_dict = {}
      form = iscsi_stgt_forms.IscsiLunForm(request.POST, zvols = zvols)
      if form.is_valid():
        cd = form.cleaned_data
        ret, err = iscsi_stgt.create_lun(cd["target_name"], cd['path'])
        if not ret:
          if err:
            return_dict["error"] = "Error creating the ISCSI LUN - %s" %err
          else:
            return_dict["error"] = "Error creating the ISCSI LUN."
          return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
        audit_str = "Created an ISCSI LUN in target %s with path %s"%(cd["target_name"], cd['path'])
        audit.audit("create_iscsi_lun", audit_str, request.META["REMOTE_ADDR"])
        url = '/view_iscsi_targets?action=lun_created'
        return django.http.HttpResponseRedirect(url)
      else:
        return_dict["form"] = form
        return django.shortcuts.render_to_response("create_iscsi_lun.html", return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def delete_iscsi_lun(request):
  return_dict = {}
  try:
    if 'target_name' not in request.REQUEST:
      return_dict["error"] = "Malformed request. No target specified. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    if 'store' not in request.REQUEST:
      return_dict["error"] = "Malformed request. No LUN specified. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

    store = request.REQUEST['store']
    target_name = request.REQUEST['target_name']

    if request.method == "GET":
      return_dict["target_name"] = target_name
      return_dict["store"] = store
      return django.shortcuts.render_to_response("delete_iscsi_lun_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      ret, err = iscsi_stgt.delete_lun(target_name, store)
      if not ret:
        if err:
          return_dict["error"] = "Error removing the ISCSI LUN - %s" %err
        else:
          return_dict["error"] = "Error removing the ISCSI LUN."
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
      audit_str = "Deleted ISCSI LUN %s from target %s"%(store, target_name)
      url = '/view_iscsi_targets?action=lun_deleted'
      audit.audit("delete_iscsi_lun", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect(url)
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def add_iscsi_user_authentication(request):
  return_dict = {}
  try:
    if 'authentication_type' not in request.REQUEST:
      return_dict["error"] = "Malformed request. No user type specified. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    if 'target_name' not in request.REQUEST:
      return_dict["error"] = "Malformed request. No target specified. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

    authentication_type = request.REQUEST['authentication_type']
    target_name = request.REQUEST['target_name']

    if authentication_type not in ['incoming', 'outgoing']:
      return_dict["error"] = "Invalid user type. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))


    if request.method == "GET":
      #Return the form
      initial = {}
      initial['authentication_type'] = authentication_type
      initial['target_name'] = target_name
      form = iscsi_stgt_forms.IscsiAuthenticationForm(initial = initial)
      return_dict["form"] = form
      return django.shortcuts.render_to_response("add_iscsi_target_user.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      #Form submission so create
      return_dict = {}
      form = iscsi_stgt_forms.IscsiAuthenticationForm(request.POST)
      if form.is_valid():
        cd = form.cleaned_data
        ret, err = iscsi_stgt.add_user_authentication(cd['target_name'], cd['authentication_type'], cd["username"], cd["password"])
        if not ret:
          if err:
            return_dict["error"] = "Error adding the ISCSI target user - %s" %err
          else:
            return_dict["error"] = "Error adding the ISCSI target user."
          return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
        if cd['authentication_type'] == 'incoming':
          audit_str = "Added ISCSI initiator authentication user %s for target %s"%(cd["username"], cd['target_name'])
          url = '/view_iscsi_targets?action=added_initiator_authentication'
        else:
          audit_str = "Added ISCSI target authentication user %s for target %s"%(cd["username"], cd['target_name'])
          url = '/view_iscsi_targets?action=added_target_authentication'
        audit.audit("add_iscsi_target_authentication", audit_str, request.META["REMOTE_ADDR"])
        return django.http.HttpResponseRedirect(url)
      else:
        return_dict["form"] = form
        return django.shortcuts.render_to_response("add_iscsi_target_user.html", return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def remove_iscsi_user_authentication(request):
  return_dict = {}
  try:
    if 'authentication_type' not in request.REQUEST:
      return_dict["error"] = "Malformed request. No user type specified. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    if 'target_name' not in request.REQUEST:
      return_dict["error"] = "Malformed request. No target specified. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    if 'username' not in request.REQUEST:
      return_dict["error"] = "Malformed request. No user name specified. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

    authentication_type = request.REQUEST['authentication_type']
    target_name = request.REQUEST['target_name']
    username = request.REQUEST['username']

    if authentication_type not in ['incoming', 'outgoing']:
      return_dict["error"] = "Invalid user type. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))


    if request.method == "GET":
      return_dict["target_name"] = target_name
      return_dict["username"] = username
      return_dict["authentication_type"] = authentication_type
      return django.shortcuts.render_to_response("remove_iscsi_user_auth_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      ret, err = iscsi_stgt.remove_user_authentication(target_name, username, authentication_type)
      if not ret:
        if err:
          return_dict["error"] = "Error removing the ISCSI authentication user - %s" %err
        else:
          return_dict["error"] = "Error removing the ISCSI authentication user."
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
      if authentication_type == 'incoming':
        audit_str = "Removed ISCSI initiator authentication user %s for target %s"%(username, target_name)
        url = '/view_iscsi_targets?action=removed_initiator_authentication'
      else:
        audit_str = "Removed ISCSI target authentication user %s for target %s"%(username, target_name)
        url = '/view_iscsi_targets?action=removed_target_authentication'
      audit.audit("remove_iscsi_target_authentication", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect(url)
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def add_iscsi_acl(request):
  return_dict = {}
  try:
    if 'target_name' not in request.REQUEST:
      return_dict["error"] = "Malformed request. No target specified. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

    target_name = request.REQUEST['target_name']
    target, err = iscsi_stgt.get_target(target_name)
    if err:
      raise Exception(err)
    if not target:
      raise Exception('Specified target not found')

    if request.method == "GET":
      #Return the form
      initial = {}
      initial['target_name'] = target_name
      form = iscsi_stgt_forms.IscsiAclForm(initial = initial)
      return_dict["form"] = form
      return django.shortcuts.render_to_response("add_iscsi_acl.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      #Form submission so create
      return_dict = {}
      form = iscsi_stgt_forms.IscsiAclForm(request.POST)
      if form.is_valid():
        cd = form.cleaned_data
        ret, err = iscsi_stgt.add_acl(cd['target_name'], cd['acl'])
        if not ret:
          if err:
            return_dict["error"] = "Error adding the ISCSI ACL - %s" %err
          else:
            return_dict["error"] = "Error adding the ISCSI ACL ."
          return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
        audit_str = "Added ISCSI ACL %s for target %s"%(cd["acl"], cd['target_name'])
        url = '/view_iscsi_targets?action=added_acl'
        audit.audit("add_iscsi_acl", audit_str, request.META["REMOTE_ADDR"])
        return django.http.HttpResponseRedirect(url)
      else:
        return_dict["form"] = form
        return django.shortcuts.render_to_response("add_iscsi_acl.html", return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def remove_iscsi_acl(request):
  return_dict = {}
  try:
    if 'acl' not in request.REQUEST:
      return_dict["error"] = "Malformed request. No ACL specified. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    if 'target_name' not in request.REQUEST:
      return_dict["error"] = "Malformed request. No target specified. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

    acl = request.REQUEST['acl']
    target_name = request.REQUEST['target_name']

    if request.method == "GET":
      return_dict["target_name"] = target_name
      return_dict["acl"] = acl
      return django.shortcuts.render_to_response("remove_iscsi_acl_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      ret, err = iscsi_stgt.remove_acl(target_name, acl)
      if not ret:
        if err:
          return_dict["error"] = "Error removing the ISCSI ACL- %s" %err
        else:
          return_dict["error"] = "Error removing the ISCSI ACL."
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
      audit_str = "Removed ISCSI ACL %s for target %s"%(acl, target_name)
      url = '/view_iscsi_targets?action=removed_acl'
      audit.audit("remove_iscsi_acl", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect(url)
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
