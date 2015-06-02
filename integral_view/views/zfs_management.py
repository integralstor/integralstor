import django, django.template

import integralstor_common
import integralstor_unicell
from integralstor_common import zfs, audit
from integralstor_unicell import nfs

import integral_view
from integral_view.forms import nfs_shares_forms
  
def view_zfs_pools(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'
    pool_list, err = zfs.get_pools()
    if not pool_list and err:
      return_dict["error"] = "Error loading ZFS storage information : %s"%err
  
    if not "error" in return_dict:
      if "action" in request.GET:
        if request.GET["action"] == "saved":
          conf = "ZFS pool information successfully updated"
        elif request.GET["action"] == "created":
          conf = "ZFS pool successfully created"
        elif request.GET["action"] == "deleted":
          conf = "ZFS pool successfully destroyed"
        return_dict["conf"] = conf
      return_dict["pool_list"] = pool_list
      template = "view_zfs_pools.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_zfs_pool(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'
    if 'name' not in request.REQUEST:
      return_dict["error"] = "Error loading ZFS pool information : No pool specified."
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
    
    pool_name = request.REQUEST['name']
    pool, err = zfs.get_pool(pool_name)

    if not pool and err:
      return_dict["error"] = "Error loading ZFS storage information : %s"%err
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
    elif not pool:
      return_dict["error"] = "Error loading ZFS storage information : Specified pool not found"
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))

    return_dict['pool'] = pool
      
    template = "view_zfs_pool.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
