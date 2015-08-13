import django, django.template

import integralstor_common
import integralstor_unicell
from integralstor_common import zfs, audit
from integralstor_unicell import nfs

import integral_view
from integral_view.forms import nfs_shares_forms
  
def view_nfs_shares(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'
    exports_list, err = nfs.load_exports_list()
    if not exports_list and err:
      return_dict["error"] = "Error loading NFS shares information : %s"%err
  
    if not "error" in return_dict:
      if "action" in request.GET:
        if request.GET["action"] == "saved":
          conf = "NFS Export information successfully updated"
        elif request.GET["action"] == "created":
          conf = "NFS Export successfully created"
        elif request.GET["action"] == "deleted":
          conf = "NFS Export successfully deleted"
        return_dict["conf"] = conf
      return_dict["exports_list"] = exports_list
      template = "view_nfs_shares.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_nfs_share(request):
  return_dict = {}
  try:
    path = request.GET['path']
    template = 'logged_in_error.html'
    if not path:
      return_dict["error"] = "Error loading NFS share - no path specified. Please use the menus."
    exports_list, err = nfs.load_exports_list()
    if not exports_list:
      return_dict["error"] = "Error loading NFS exports information : "
      if err:
        return_dict["error"] += err
    found = False
    print exports_list
    for e in exports_list:
      if e['path'] == path:
        found = True
        return_dict['share_info'] = e
        break
    if not found:
      return_dict["error"] = "Error loading NFS share information : Requested share not found."
  
    if not "error" in return_dict:
      template = "view_nfs_share.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def delete_nfs_share(request):

  return_dict = {}
  try:
    if request.method == "GET":
      #Return the conf page
      path = request.GET["path"]
      return_dict["path"] = path
      return django.shortcuts.render_to_response("delete_nfs_share_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      path = request.POST["path"]
      #logger.debug("Delete share request for name %s"%name)
      try :
        result, err = nfs.delete_share(path)
        if not result:
          if not err:
            raise Exception('Unknown error!')
          else:
            raise Exception(err)
      except Exception, e:
        return_dict["error"] = "Error deleting NFS share - %s"%str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
 
      audit_str = "Deleted NFS share %s"%path
      audit.audit("delete_nfs_share", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_nfs_shares?action=deleted')
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def edit_nfs_share(request):
  return_dict = {}
  try:
    if request.method == "GET":
      #Return the conf page
      path = request.GET["path"]
      d, err = nfs.get_share(path)
      if not d:
        raise Exception('Could not find the specified share. Please use the menus. : %s'%err)
      initial = {}
      initial['path'] = d['path']
      if 'clients' in d:
        client_list = []
        for client in d['clients']:
          client_list.append(client['name'])
        initial['clients'] = ','.join(client_list)
      initial['readonly'] = False
      initial['root_squash'] = False
      initial['all_squash'] = False
      if 'options' in d:
        for option in d['options']:
          if option == 'ro':
            initial['readonly'] = True
          elif option == 'root_squash':
            initial['root_squash'] = True
          elif option == 'all_squash':
            initial['all_squash'] = True
      form = nfs_shares_forms.ShareForm(initial=initial)
      return_dict['form'] = form
      return django.shortcuts.render_to_response("edit_nfs_share.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = nfs_shares_forms.ShareForm(request.POST)
      path = request.POST["path"]
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("edit_nfs_share.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      try :
        result, err = nfs.save_share(cd)
        if not result:
          if not err:
            raise Exception('Unknown error!')
          else:
            raise Exception(err)
      except Exception, e:
        return_dict["error"] = "Error saving NFS share information - %s"%str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
 
      audit_str = "Edited NFS share %s"%path
      audit.audit("edit_nfs_share", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_nfs_shares?action=saved')
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_nfs_share(request):
  return_dict = {}
  try:
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
      #Return the conf page
      form = nfs_shares_forms.ShareForm(dataset_list = ds_list)
      return_dict['form'] = form
      return django.shortcuts.render_to_response("create_nfs_share.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = nfs_shares_forms.ShareForm(request.POST, dataset_list = ds_list)
      path = request.POST["path"]
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("create_nfs_share.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      try :
        result, err = nfs.save_share(cd, True)
        if not result:
          if not err:
            raise Exception('Unknown error!')
          else:
            raise Exception(err)
      except Exception, e:
        return_dict["error"] = "Error creating NFS share information - %s"%str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
 
      audit_str = "Created NFS share %s"%path
      audit.audit("create_nfs_share", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_nfs_shares?action=created')
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
