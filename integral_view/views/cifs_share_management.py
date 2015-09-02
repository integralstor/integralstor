
import django, django.template

import integral_view, os
from integral_view.forms import samba_shares_forms
from integral_view.samba import samba_settings


from integralstor_common import audit, networking,zfs

def view_cifs_shares(request):

  return_dict = {}
  try:
    template = 'logged_in_error.html'
    shares_list, err = samba_settings.load_shares_list()
    if err:
      raise Exception(err)
  
    if not "error" in return_dict:
      if "action" in request.GET:
        if request.GET["action"] == "saved":
          conf = "Share information successfully updated"
        elif request.GET["action"] == "created":
          conf = "Share successfully created"
        elif request.GET["action"] == "deleted":
          conf = "Share successfully deleted"
        return_dict["conf"] = conf
      return_dict["shares_list"] = shares_list
      template = "view_cifs_shares.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))



def view_cifs_share(request):

  return_dict = {}
  try:
    template = 'logged_in_error.html'
  
    if request.method != "GET":
      raise Exception("Incorrect access method. Please use the menus")
  
    if "index" not in request.GET or "access_mode" not in request.GET:
      raise Exception("Insufficient parameters. Please use the menus")
  
    access_mode = request.GET["access_mode"]
    index = request.GET["index"]
  
    if "action" in request.GET and request.GET["action"] == "saved":
      return_dict["conf_message"] = "Information updated successfully"
  
    valid_users_list = None
    share, err = samba_settings.load_share_info(access_mode, index)
    if err:
      raise Exception(err)
    if not share:
      raise Exception('Specified share not found')

    valid_users_list, err = samba_settings.load_valid_users_list(share["share_id"])
    if err:
      raise Exception(err)
    if not share:
      raise Exception("Error retrieving share information for  %s" %share_name)

    return_dict["share"] = share
    if valid_users_list:
        return_dict["valid_users_list"] = valid_users_list
    template = 'view_cifs_share.html'
  
    return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def edit_cifs_share(request):

  return_dict = {}
  try:
    user_list, err = samba_settings.get_user_list()
    if err:
      raise Exception(err)
    group_list, err = samba_settings.get_group_list()
    if err:
      raise Exception(err)

    if request.method == "GET":
      # Shd be an edit request
      if "share_id" not in request.GET:
        return_dict["error"] = "Unknown share specified"
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
      share_id = request.GET["share_id"]
      share_dict, err = samba_settings.load_share_info("by_id", share_id)
      if err:
        raise Exception(err)
      valid_users_list, err = samba_settings.load_valid_users_list(share_dict["share_id"])
      if err:
        raise Exception(err)
  
      # Set initial form values
      initial = {}
      initial["share_id"] = share_dict["share_id"]
      initial["name"] = share_dict["name"]
      initial["path"] = share_dict["path"]
      if share_dict["guest_ok"]:
        initial["guest_ok"] = True
      else:
        initial["guest_ok"] = False
      if share_dict["browseable"]:
        initial["browseable"] = True
      else:
        initial["browseable"] = False
      if share_dict["read_only"]:
        initial["read_only"] = True
      else:
        initial["read_only"] = False
      initial["comment"] = share_dict["comment"]
  
      if valid_users_list:
        vgl = []
        vul = []
        for u in valid_users_list:
          if u["grp"]:
            vgl.append(u["name"])
          else:
            vul.append(u["name"])
        initial["users"] = vul
        initial["groups"] = vgl
  
      form = samba_shares_forms.EditShareForm(initial = initial, user_list = user_list, group_list = group_list)
  
      return_dict["form"] = form
      return django.shortcuts.render_to_response('edit_cifs_share.html', return_dict, context_instance=django.template.context.RequestContext(request))
  
    else:
  
      # Shd be an save request
      form = samba_shares_forms.EditShareForm(request.POST, user_list = user_list, group_list = group_list)
      return_dict["form"] = form
      if form.is_valid():
        cd = form.cleaned_data
        name = cd["name"]
        share_id = cd["share_id"]
        path = cd["path"]
        if "comment" in cd:
          comment = cd["comment"]
        else:
          comment = None
        if "read_only" in cd:
          read_only = cd["read_only"]
        else:
          read_only = False
        if "browseable" in cd:
          browseable = cd["browseable"]
        else:
          browseable = False
        if "guest_ok" in cd:
          guest_ok = cd["guest_ok"]
        else:
          guest_ok = False
        if "users" in cd:
          users = cd["users"]
        else:
          users = None
        if "groups" in cd:
          groups = cd["groups"]
        else:
          groups = None
        #logger.debug("Save share request, name %s path %s, comment %s, read_only %s, browseable %s, guest_ok %s, users %s, groups %s, vol %s"%(name, path, comment, read_only, browseable, guest_ok, users, groups))
        ret, err = samba_settings.save_share(share_id, name, comment, guest_ok, read_only, path, browseable, users, groups)
        if err:
          raise Exception(err)
        ret, err = samba_settings.generate_smb_conf()
        if err:
          raise Exception(err)
  
        audit_str = "Modified share %s"%cd["name"]
        audit.audit("modify_cifs_share", audit_str, request.META["REMOTE_ADDR"])
  
        return django.http.HttpResponseRedirect('/view_cifs_share?access_mode=by_id&index=%s&action=saved'%cd["share_id"])
  
      else:
        #Invalid form
        return django.shortcuts.render_to_response('edit_cifs_share.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


  
def delete_cifs_share(request):
  
  return_dict = {}
  try:
    if request.method == "GET":
      #Return the conf page
      share_id = request.GET["share_id"]
      name = request.GET["name"]
      return_dict["share_id"] = share_id
      return_dict["name"] = name
      return django.shortcuts.render_to_response("delete_cifs_share_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      share_id = request.POST["share_id"]
      name = request.POST["name"]
      #logger.debug("Delete share request for name %s"%name)
      ret, err = samba_settings.delete_share(share_id)
      if err:
        raise Exception(err)
      ret, err = samba_settings.generate_smb_conf()
      if err:
        raise Exception(err)
  
      audit_str = "Deleted CIFS share %s"%name
      audit.audit("delete_cifs_share", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_cifs_shares?action=deleted')
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_cifs_share(request):

  return_dict = {}
  try:
    user_list, err = samba_settings.get_user_list()
    if err:
      raise Exception(err)
    group_list, err = samba_settings.get_group_list()
    if err:
      raise Exception(err)
    pools, err = zfs.get_pools()
    if err:
      raise Exception('No ZFS pools available. Please create a pool and dataset before creating shares.')

    ds_list = [] 
    for pool in pools:
      for ds in pool["datasets"]:
        if ds['properties']['type']['value'] == 'filesystem':
          ds_list.append({'name': ds["name"], 'mountpoint': ds["mountpoint"]})
    if not ds_list:
      raise Exception('No ZFS datasets available. Please create a dataset before creating shares.')
  
    if request.method == "GET":
      #Return the form

      form = samba_shares_forms.CreateShareForm(user_list = user_list, group_list = group_list, dataset_list = ds_list, initial = {'guest_ok': True})
      return_dict["form"] = form

      return django.shortcuts.render_to_response("create_cifs_share.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      #Form submission so create
      return_dict = {}
      form = samba_shares_forms.CreateShareForm(request.POST, user_list = user_list, group_list = group_list, dataset_list = ds_list)
      return_dict["form"] = form
      if form.is_valid():
        cd = form.cleaned_data
        name = cd["name"]
        path = "%s"%cd["path"]
        if not path:
          return_dict["path_error"] = "Please choose a path."
          return django.shortcuts.render_to_response("create_cifs_share.html", return_dict, context_instance = django.template.context.RequestContext(request))
        display_path = cd["display_path"]    
        if not os.path.isdir(display_path):
          os.mkdir(display_path)
        if "comment" in cd:
          comment = cd["comment"]
        else:
          comment = None
        if "read_only" in cd:
          read_only = cd["read_only"]
        else:
          read_only = None
        if "browseable" in cd:
          browseable = cd["browseable"]
        else:
          browseable = None
        if "guest_ok" in cd:
          guest_ok = cd["guest_ok"]
        else:
          guest_ok = None
        if "users" in cd:
          users = cd["users"]
        else:
          users = None
        if "groups" in cd:
          groups = cd["groups"]
        else:
          groups = None
        vol = "unicell"
        #logger.debug("Create share request, name %s path %s, comment %s, read_only %s, browseable %s, guest_ok %s, users %s, groups %s, vol %s"%(name, path, comment, read_only, browseable, guest_ok, users, groups))
        print '1'
        ret, err = samba_settings.create_share(name, comment, guest_ok, read_only, display_path, display_path, browseable, users, groups,vol)
        print '2'
        if err:
          raise Exception(err)
        ret, err = samba_settings.generate_smb_conf()
        print '3'
        if err:
          raise Exception(err)
  
        audit_str = "Created Samba share %s"%name
        audit.audit("create_cifs_share", audit_str, request.META["REMOTE_ADDR"])
        return django.http.HttpResponseRedirect('/view_cifs_shares?action=created')
      else:
        return django.shortcuts.render_to_response("create_cifs_share.html", return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def samba_server_settings(request):

  return_dict = {}
  #print 'a1'
  try:
    d, err = samba_settings.load_auth_settings()
    if err:
      raise Exception(err)
  
    if "action" in request.REQUEST and request.REQUEST["action"] == "edit":
      ini = {}
      if d:    
        for k in d.keys():
          ini[k] = d[k] 
      if d and d["security"] == "ads":
        form = samba_shares_forms.AuthADSettingsForm(initial=ini)
      #elif d["security"] == "users":
      else:
        #print 'c'
        form = samba_shares_forms.AuthUsersSettingsForm(initial=ini)
        #print 'd'
      return_dict["form"] = form
      return django.shortcuts.render_to_response('edit_samba_server_settings.html', return_dict, context_instance=django.template.context.RequestContext(request))
  
    # Else a view request
    return_dict["samba_global_dict"] = d
    #print 'a2'
  
    if "action" in request.REQUEST and request.REQUEST["action"] == "saved":
      return_dict["conf"] = "Information updated successfully"
    return django.shortcuts.render_to_response('view_samba_server_settings.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def edit_auth_method(request):
  return_dict = {}
  try:
    d, err = samba_settings.load_auth_settings()
    if err:
      raise Exception(err)
    return_dict["samba_global_dict"] = d
  
    if request.method == "GET":
      return django.shortcuts.render_to_response('edit_auth_method.html', return_dict, context_instance=django.template.context.RequestContext(request))
    else:
      #Save request
      if "auth_method" not in request.POST:
        return_dict["error"] = "Please select an authentication method" 
        return django.shortcuts.render_to_response('edit_auth_method.html', return_dict, context_instance=django.template.context.RequestContext(request))
      security = request.POST["auth_method"]
      if security == d["security"]:
        return_dict["error"] = "Selected authentication method is the same as before." 
        return django.shortcuts.render_to_response('edit_auth_method.html', return_dict, context_instance=django.template.context.RequestContext(request))
  
      ret, err = samba_settings.change_auth_method(security)
      if err:
        raise Exception(err)
      ret, err = samba_settings.generate_smb_conf()
      if err:
        raise Exception(err)
  
    return django.http.HttpResponseRedirect('/auth_server_settings?action=edit')
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
  


def save_samba_server_settings(request):

  return_dict = {}
  try:
    if request.method != "POST":
      return_dict["error"] = "Invalid access method. Please try again using the menus"
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
  
    if "security" not in request.POST:
      return_dict["error"] = "Invalid security specification. Please try again using the menus"
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
  
    if request.POST["security"] == "ads":
      form = samba_shares_forms.AuthADSettingsForm(request.POST)
    elif request.POST["security"] == "users":
      form = samba_shares_forms.AuthUsersSettingsForm(request.POST)
    else:
      return_dict["error"] = "Invalid security specification. Please try again using the menus"
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
  
    return_dict["form"] = form
    return_dict["action"] = "edit"
  
    if form.is_valid():
      cd = form.cleaned_data
  
      ret, err = samba_settings.save_auth_settings(cd)
      if err:
        raise Exception(err)
      if cd["security"] == "ads":
        ret, err = samba_settings.generate_krb5_conf()
        if err:
          raise Exception(err)
      ret, err = samba_settings.generate_smb_conf()
      if err:
        raise Exception(err)
      if cd["security"] == "ads":
        rc, err = samba_settings.kinit("administrator", cd["password"], cd["realm"])
        if err:
          raise Exception(err)
        rc, err = samba_settings.net_ads_join("administrator", cd["password"], cd["password_server"])
        if err:
          raise Exception(err)
      ret, err = samba_settings.restart_samba_services()
      if err:
        raise Exception(err)
      #print '6'
    else:
      return django.shortcuts.render_to_response('edit_samba_server_settings.html', return_dict, context_instance=django.template.context.RequestContext(request))
  
    #print '7'
    audit_str = "Modified share authentication settings"
    audit.audit("modify_samba_settings", audit_str, request.META["REMOTE_ADDR"])
    return_dict["form"] = form
    return_dict["conf_message"] = "Information successfully updated"
    #print '8'
    return django.http.HttpResponseRedirect('/auth_server_settings?action=saved')
    #return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


