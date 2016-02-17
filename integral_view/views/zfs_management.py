import django, django.template

import integralstor_common
import integralstor_unicell
from integralstor_common import zfs, audit, ramdisk,file_processing, common, command
from integralstor_common import scheduler_utils, manifest_status
from integralstor_common import cifs as common_cifs
from integralstor_unicell import nfs,local_users, iscsi_stgt, system_info

import json, time, os, shutil, tempfile, os.path, re, subprocess, sys, shutil, pwd, grp, stat,datetime

from integral_view.forms import zfs_forms,common_forms
  
def view_zfs_pools(request):
  return_dict = {}
  try:
    template = "view_zfs_pools.html"
    pool_list, err = zfs.get_pools()
    if err:
      raise Exception(err)
  
    if "action" in request.GET:
      if request.GET["action"] == "saved":
        conf = "ZFS pool information successfully updated"
      elif request.GET["action"] == "expanded_pool":
        conf = "ZFS pool successfully expanded"
      elif request.GET["action"] == "pool_exported":
        conf = "ZFS pool successfully exported"
      elif request.GET["action"] == "imported_pool":
        conf = "ZFS pool successfully imported"
      elif request.GET["action"] == "set_quota":
        conf = "ZFS quota successfully set"
      elif request.GET["action"] == "removed_quota":
        conf = "ZFS quota successfully removed"
      elif request.GET["action"] == "created_pool":
        conf = "ZFS pool successfully created"
      elif request.GET["action"] == "set_permissions":
        conf = "Directory ownership/permissions successfully set"
      elif request.GET["action"] == "created_dataset":
        conf = "ZFS dataset successfully created"
      elif request.GET["action"] == "created_zvol":
        conf = "ZFS block device volume successfully created"
      elif request.GET["action"] == "pool_deleted":
        conf = "ZFS pool successfully destroyed"
      elif request.GET["action"] == "pool_scrub_initiated":
        conf = "ZFS pool scrub successfully initiated"
      elif request.GET["action"] == "dataset_deleted":
        conf = "ZFS dataset successfully destroyed"
      elif request.GET["action"] == "zvol_deleted":
        conf = "ZFS block device volume successfully destroyed"
      elif request.GET["action"] == "slog_deleted":
        conf = "ZFS write cache successfully removed"
      elif request.GET["action"] == "changed_slog":
        conf = "ZFS pool write cache successfully set"
      elif request.GET["action"] == "added_spares":
        conf = "Successfully added spare disks to the pool"
      elif request.GET["action"] == "removed_spare":
        conf = "Successfully removed a spare disk from the pool"
      if conf:
        return_dict["conf"] = conf
    return_dict["pool_list"] = pool_list
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'ZFS pools'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error loading ZFS pools'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_zfs_pool(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'
    if 'name' not in request.REQUEST:
      raise Exception("No pool specified.")
    
    if "action" in request.GET:
      if request.GET["action"] == "saved":
        conf = "ZFS pool information successfully updated"
      elif request.GET["action"] == "expanded_pool":
        conf = "ZFS pool successfully expanded"
      elif request.GET["action"] == "set_quota":
        conf = "ZFS quota successfully set"
      elif request.GET["action"] == "removed_quota":
        conf = "ZFS quota successfully removed"
      elif request.GET["action"] == "set_permissions":
        conf = "Directory ownership/permissions successfully set"
      elif request.GET["action"] == "created_dataset":
        conf = "ZFS dataset successfully created"
      elif request.GET["action"] == "created_zvol":
        conf = "ZFS block device volume successfully created"
      elif request.GET["action"] == "pool_scrub_initiated":
        conf = "ZFS pool scrub successfully initiated"
      elif request.GET["action"] == "dataset_deleted":
        conf = "ZFS dataset successfully destroyed"
      elif request.GET["action"] == "zvol_deleted":
        conf = "ZFS block device volume successfully destroyed"
      elif request.GET["action"] == "slog_deleted":
        conf = "ZFS write cache successfully removed"
      elif request.GET["action"] == "l2arc_deleted":
        conf = "ZFS read cache successfully removed"
      elif request.GET["action"] == "changed_slog":
        conf = "ZFS pool write cache successfully set"
      elif request.GET["action"] == "changed_l2arc":
        conf = "ZFS pool read cache successfully set"
      elif request.GET["action"] == "added_spares":
        conf = "Successfully added spare disks to the pool"
      elif request.GET["action"] == "removed_spare":
        conf = "Successfully removed a spare disk from the pool"
      if conf:
        return_dict["conf"] = conf

    pool_name = request.REQUEST['name']
    pool, err = zfs.get_pool(pool_name)
    #print pool.keys()

    if err:
      raise Exception(err)
    elif not pool:
      raise Exception("Specified pool not found")

    num_free_disks_for_spares, err = zfs.get_free_disks_for_spares(pool_name)
    if err:
      raise Exception(err)

    snap_list, err = zfs.get_snapshots(pool_name)
    if err:
      raise Exception(err)

    (can_expand, new_pool_type), err = zfs.can_expand_pool(pool_name)

    quotas, err = zfs.get_all_quotas(pool_name)
    if err:
      raise Exception(err)

    schedule, err = zfs.get_snapshot_schedule(pool_name)
    if err:
      raise Exception(err)

    return_dict['snapshot_schedule'] = schedule
    return_dict['can_expand_pool'] = can_expand
    return_dict['num_free_disks_for_spares'] = num_free_disks_for_spares
    return_dict['snap_list'] = snap_list
    return_dict['pool'] = pool
    return_dict['pool_name'] = pool_name
    return_dict['quotas'] = quotas
      
    template = "view_zfs_pool.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'ZFS pool details'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error loading ZFS pool details'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def set_zfs_quota(request):
  return_dict = {}
  try:
    if 'path' not in request.REQUEST or 'ug_type' not in request.REQUEST or 'path_type' not in request.REQUEST:
      raise Exception("Malformed request. Please use the menus")
    path_type = request.REQUEST["path_type"]
    path = request.REQUEST["path"]
    ug_type = request.REQUEST["ug_type"]
    pool_name = request.REQUEST["pool_name"]
    if ug_type not in ['user', 'group']:
      raise Exception("Malformed request. Please use the menus")
    if ug_type == 'user':
      ugl, err = local_users.get_local_users()
    else:
      ugl, err = local_users.get_local_groups()
    if err:
      raise Exception(err)
    ug_list = []
    for ug in ugl:
      if ug_type == 'user':
        ug_list.append(ug['username'])
      else:
        ug_list.append(ug['grpname'])
    return_dict["path"] = path
    return_dict["pool_name"] = pool_name
    return_dict["path_type"] = path_type
    return_dict["ug_type"] = ug_type
    if request.method == "GET":
      form = zfs_forms.QuotaForm(user_group_list = ug_list, initial={'ug_type': ug_type, 'path':path})
      return_dict['form'] = form
      return django.shortcuts.render_to_response("set_zfs_quota.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = zfs_forms.QuotaForm(request.POST, user_group_list = ug_list)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("set_zfs_quota.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      if cd['ug_type'] == 'user':
        user = True
      else:
        user = False
      ret, err = zfs.set_quota(cd['path'], cd['ug_name'], '%d%s'%(cd['size'], cd['unit']), user)
      if err:
        raise Exception(err)
      audit_str = "Set ZFS quota for %s %s for %s to %s%s"%(cd['ug_type'], cd['ug_name'], cd['path'], cd['size'], cd['unit'])
      audit.audit("set_zfs_quota", audit_str, request.META["REMOTE_ADDR"])
      if path_type == 'pool':
        return django.http.HttpResponseRedirect('/view_zfs_pool?action=set_quota&name=%s'%pool_name)
      else:
        return django.http.HttpResponseRedirect('/view_zfs_dataset?action=set_quota&name=%s'%path)
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Setting ZFS quota'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error setting ZFS quota'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def remove_zfs_quota(request):
  return_dict = {}
  try:
    if 'path' not in request.REQUEST or 'ug_name' not in request.REQUEST or 'ug_type' not in request.REQUEST or 'path_type' not in request.REQUEST:
      raise Exception("Malformed request. Please use the menus")
    path = request.REQUEST["path"]
    path_type = request.REQUEST["path_type"]
    pool_name = request.REQUEST["pool_name"]
    ug_name = request.REQUEST["ug_name"]
    ug_type = request.REQUEST["ug_type"]

    return_dict["path"] = path
    return_dict["pool_name"] = pool_name
    return_dict["path_type"] = path_type
    return_dict["ug_name"] = ug_name
    return_dict["ug_type"] = ug_type
    if request.method == "GET":
      #Return the conf page
      return django.shortcuts.render_to_response("remove_zfs_quota_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      if ug_type == 'user':
        user = True
      else:
        user = False
      result, err = zfs.set_quota(path, ug_name, 'none', user)
      if not result:
        if not err:
          raise Exception('Unknown error!')
        else:
          raise Exception(err)
 
      audit_str = "Removed ZFS quota for %s %s for %s"%(ug_type, ug_name, path)
      audit.audit("remove_zfs_quota", audit_str, request.META["REMOTE_ADDR"])
      if path_type == 'pool':
        return django.http.HttpResponseRedirect('/view_zfs_pool?action=removed_quota&name=%s'%pool_name)
      else:
        return django.http.HttpResponseRedirect('/view_zfs_dataset?action=removed_quota&name=%s'%path)
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Removing ZFS quota'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error removing ZFS quota'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def export_zfs_pool(request):
  return_dict = {}
  try:
    if 'pool_name' not in request.REQUEST:
      raise Exception("Malformed request. Please use the menus")
    pool_name = request.REQUEST["pool_name"]

    return_dict["pool_name"] = pool_name
    if request.method == "GET":
      #Return the conf page
      return django.shortcuts.render_to_response("export_zfs_pool_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      result, err = zfs.export_pool(pool_name)
      if not result:
        if not err:
          raise Exception('Unknown error!')
        else:
          raise Exception(err)
 
      audit_str = 'Exported ZFS pool "%s"'%pool_name
      audit.audit("export_zfs_pool", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_pools?action=pool_exported')
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Export ZFS pool'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error exporting ZFS pool'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def import_all_zfs_pools(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'
    
    output, err = command.get_command_output('zpool import -maf')
    if err:
      raise Exception(err)

    return_dict['output'] = output
      
    template = "import_pool_from_disks_result.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Import all ZFS pools'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error importing all ZFS pool(s) from disks'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def import_zfs_pool(request):
  return_dict = {}
  try:
    if request.method == 'GET':
      form = zfs_forms.ImportPoolForm()
      return_dict['form'] = form
      return django.shortcuts.render_to_response("import_zfs_pool.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = zfs_forms.ImportPoolForm(request.POST)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("import_zfs_pool.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      ret, err = zfs.import_pool(cd['name'])
      if err:
        raise Exception(err)
      audit_str = 'Imported a ZFS pool named "%s" '%(cd['name'])
      audit.audit("import_zfs_pool", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_pools?action=imported_pool')
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Import a ZFS pool'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error importing a specific ZFS pool from disks'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_zfs_pool(request):
  return_dict = {}
  try:

    free_disks, err = zfs.get_free_disks()
    if err:
      raise Exception(err)

    if not free_disks or len(free_disks) < 2:
      raise Exception('There are insufficient unused disks available to create a pool')

    pool_types = []
    if len(free_disks) >= 2 :
      pool_types.append(('mirror', 'MIRROR'))
    if len(free_disks) >= 3 :
      pool_types.append(('raid5', 'RAID-5'))
    if len(free_disks) >= 4 :
      pool_types.append(('raid6', 'RAID-6'))
      pool_types.append(('raid10', 'RAID-10'))
    if len(free_disks) >= 6 :
      pool_types.append(('raid50', 'RAID-50'))
    if len(free_disks) >= 8 :
      pool_types.append(('raid60', 'RAID-60'))

    if request.method == "GET":
      #Return the conf page
      form = zfs_forms.CreatePoolForm(pool_types = pool_types, num_free_disks = len(free_disks), initial={'num_disks': len(free_disks)})
      return_dict['form'] = form
      return_dict['num_disks'] = len(free_disks)
      return django.shortcuts.render_to_response("create_zfs_pool.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = zfs_forms.CreatePoolForm(request.POST, pool_types = pool_types, num_free_disks = len(free_disks))
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("create_zfs_pool.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      #print cd
      vdev_list = None
      if cd['pool_type'] in ['raid5', 'raid6']:
        vdev_list, err = zfs.create_pool_data_vdev_list(cd['pool_type'], disk_type = cd['disk_type'], num_raid_disks = cd['num_raid_disks'])
      elif cd['pool_type'] == 'raid10':
        vdev_list, err = zfs.create_pool_data_vdev_list(cd['pool_type'], disk_type = cd['disk_type'], stripe_width = cd['stripe_width'])
      elif cd['pool_type'] in ['raid50', 'raid60']:
        vdev_list, err = zfs.create_pool_data_vdev_list(cd['pool_type'], disk_type = cd['disk_type'], num_raid_disks = cd['num_raid_disks'], stripe_width = cd['stripe_width'])
      else:
        vdev_list, err = zfs.create_pool_data_vdev_list(cd['pool_type'], disk_type = cd['disk_type'])
      if err:
        raise Exception(err)
      #print 'vdevlist', vdev_list
      result, err = zfs.create_pool(cd['name'], cd['pool_type'], vdev_list)
      if not result:
        if not err:
          raise Exception('Unknown error!')
        else:
          raise Exception(err)
 
      audit_str = "Created a ZFS pool named %s of type %s"%(cd['name'], cd['pool_type'])
      audit.audit("create_zfs_pool", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_pools?action=created_pool')
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'ZFS pool creation'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error creating a ZFS pool'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def expand_zfs_pool(request):
  return_dict = {}
  try:
    if 'pool_name' not in request.REQUEST:
      raise Exception('Pool not specified. Please use the menus.')
    pool_name = request.REQUEST['pool_name']
    if request.method == 'GET':
      (can_expand, new_pool_type), err = zfs.can_expand_pool(pool_name)
      if err:
        raise Exception(err)
      if not can_expand:
        raise Exception('Cannot expand the specified pool.')
      return_dict['new_pool_type'] = new_pool_type
      return_dict['pool_name'] = pool_name
      return django.shortcuts.render_to_response("expand_zfs_pool_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      ret, err = zfs.expand_pool(pool_name)
      if err:
        raise Exception(err)
      audit_str = "Expanded the ZFS pool named %s"%pool_name
      audit.audit("expand_zfs_pool", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_pool?action=expanded_pool&name=%s'%pool_name)
  
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'ZFS pool expansion'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error expanding a ZFS pool'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def scrub_zfs_pool(request):

  return_dict = {}
  try:
    if 'name' not in request.REQUEST:
      raise Exception("No pool specified. Please use the menus")
    name = request.REQUEST["name"]
    return_dict["name"] = name
    if request.method == "GET":
      #Return the conf page
      return django.shortcuts.render_to_response("scrub_zfs_pool_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      result, err = zfs.scrub_pool(name)
      if not result:
        if not err:
          raise Exception('Unknown error!')
        else:
          raise Exception(err)
 
      audit_str = "ZFS pool scrub initiated on pool %s"%name
      audit.audit("scrub_zfs_pool", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_pool?action=pool_scrub_initiated&name=%s'%name)
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'ZFS pool scrub'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error scrubbing ZFS pool'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def delete_zfs_pool(request):

  return_dict = {}
  try:
    if 'name' not in request.REQUEST:
      raise Exception("No pool specified. Please use the menus")
    name = request.REQUEST["name"]
    nfs_shares, err = nfs.get_shares_on_subpath('%s/'%name)
    if err:
      raise Exception(err)
    cifs_shares, err = common_cifs.get_shares_on_subpath('%s/'%name)
    if err:
      raise Exception(err)
    luns, err = iscsi_stgt.get_luns_on_subpath('%s/'%name)
    if err:
      raise Exception(err)
    if nfs_shares or cifs_shares or luns:
      elements = []
      if nfs_shares:
        shl=[]
        for sh in nfs_shares:
          shl.append(sh['path'])
        elements .append('NFS share(s) : %s'%' , '.join(shl))
      if cifs_shares:
        print '1'
        shl=[]
        for sh in cifs_shares:
          shl.append(sh['name'])
        elements .append('CIFS share(s) : %s'%' , '.join(shl))
        print '2'
      if luns:
        shl=[]
        for sh in luns:
          print sh
          shl.append(sh['path'][9:])
        elements .append('ISCSI LUN(s) : %s'%' , '.join(shl))
        print '3'
      raise Exception('The pool cannot be deleted as the following components exist on this pool : %s. Please delete them first before deleting the pool.'%' , '.join(elements))
    return_dict["name"] = name
    if request.method == "GET":
      #Return the conf page
      return django.shortcuts.render_to_response("delete_zfs_pool_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      result, err = zfs.delete_pool(name)
      if not result:
        if not err:
          raise Exception('Unknown error!')
        else:
          raise Exception(err)
 
      audit_str = "Deleted ZFS pool %s"%name
      audit.audit("delete_zfs_pool", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_pools?action=pool_deleted')
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Remove a ZFS pool'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error removing a ZFS pool'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def set_zfs_slog(request):
  return_dict = {}
  try:
    
    template = 'logged_in_error.html'

    if 'pool' not in request.REQUEST:
      raise Exception("No pool specified.")

    pool_name = request.REQUEST["pool"]

    pool, err = zfs.get_pool(pool_name)

    if err:
      raise Exception(err)
    elif not pool:
      raise Exception("Error loading ZFS storage information : Specified pool not found")

    slog = None
    if not pool['config']['logs']:
      slog = None
    else:
      kids = pool['config']['logs']['root']['children']
      if len(kids) == 1 and 'ramdisk' in kids[0]:
        slog = 'ramdisk'
        rdisk, err = ramdisk.get_ramdisk_info('/mnt/ramdisk_%s'%pool_name)
        if err:
          raise Exception(err)
        elif not rdisk:
          raise Exception("Could not determine the configuration for the RAM disk for the specified ZFS pool")
        ramdisk_size = rdisk['size']/1024
      else:
        #For now pass but we need to code this to read the component disk ID!!!!!!!!!!!!1
        slog = 'flash'
    free_disks, err = zfs.get_free_disks(disk_type = 'flash')
    print free_disks
    if err:
      raise Exception(err)

    if request.method == "GET":
      #Return the conf page

      initial = {}
      initial['pool'] = pool_name
      initial['slog'] = slog
      if slog == 'ramdisk':
        initial['ramdisk_size'] = ramdisk_size

      form = zfs_forms.SlogForm(initial=initial, free_disks = free_disks)
      return_dict['form'] = form
      return django.shortcuts.render_to_response("edit_zfs_slog.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = zfs_forms.SlogForm(request.POST, free_disks = free_disks)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("edit_zfs_slog.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      #print cd
      if cd['slog'] == 'ramdisk':
        if ((cd['slog'] == slog) and (cd['ramdisk_size'] != ramdisk_size)) or (cd['slog'] != slog):
          # Changed to ramdisk or ramdisk parameters changed so destroy and recreate
          oldramdisk, err = ramdisk.get_ramdisk_info('/mnt/ramdisk_%s'%cd['pool'])
          if err:
            raise Exception(err)
          if oldramdisk:
            result, err = ramdisk.destroy_ramdisk('/mnt/ramdisk_%s'%cd['pool'], cd['pool'])
            if err:
              raise Exception(err)
            result, err = zfs.remove_pool_vdev(cd['pool'], '/mnt/ramdisk_%s/ramfile'%cd['pool'])
            if err:
              raise Exception(err)
          result, err = ramdisk.create_ramdisk(1024*cd['ramdisk_size'], '/mnt/ramdisk_%s'%cd['pool'], cd['pool'])
          if err:
            raise Exception(err)
          else:
            result, err = zfs.set_pool_log_vdev(cd['pool'], '/mnt/ramdisk_%s/ramfile'%cd['pool'])
            if err:
              ramdisk.destroy_ramdisk('/mnt/ramdisk_%s'%cd['pool'], cd['pool'])
              raise Exception(err)
            audit.audit("edit_zfs_slog", 'Changed the write log for pool %s to a RAM disk of size %dGB'%(cd['pool'], cd['ramdisk_size']), request.META["REMOTE_ADDR"])
      else:
        #Flash drive          
        result, err = zfs.set_pool_log_vdev(cd['pool'], cd['disk'])
        if err:
          raise Exception(err)
        audit.audit("edit_zfs_slog", 'Changed the write log for pool %s to a flash drive'%(cd['pool']), request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_pool?action=changed_slog&name=%s'%pool_name)
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Set ZFS pool write cache'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error setting ZFS pool write cache'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def remove_zfs_slog(request):

  return_dict = {}
  try:
    if 'pool' not in request.REQUEST:
      raise Exception("No pool specified. Please use the menus")
    if 'device' not in request.REQUEST:
      raise Exception("No device specified. Please use the menus")
    pool = request.REQUEST["pool"]
    return_dict["pool"] = pool
    device = request.REQUEST["device"]
    type = request.REQUEST["type"]
    return_dict["device"] = device
    return_dict["type"] = type
    if request.method == "GET":
      #Return the conf page
      return django.shortcuts.render_to_response("remove_zfs_slog_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      result, err = zfs.remove_pool_vdev(pool, device)
      if not result:
        if not err:
          raise Exception('Unknown error!')
        else:
          raise Exception(err)
      if type == 'ramdisk':
        result, err = ramdisk.destroy_ramdisk('/mnt/ramdisk_%s'%pool, pool)
        if err:
          raise Exception(err)
 
      audit_str = "Removed ZFS write cache for pool %s"%pool
      audit.audit("remove_zfs_slog", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_pool?name=%s&action=slog_deleted'%pool)
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Removing ZFS pool write cache'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error removing ZFS pool write cache'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def set_zfs_l2arc(request):
  return_dict = {}
  try:
    

    if 'pool' not in request.REQUEST:
      raise Exception("No pool specified.")

    pool_name = request.REQUEST["pool"]

    pool, err = zfs.get_pool(pool_name)

    if err:
      raise Exception(err)
    elif not pool:
      raise Exception("Error loading ZFS storage information : Specified pool not found")

    free_disks, err = zfs.get_free_disks(disk_type = 'flash')
    if err:
      raise Exception(err)
    #print free_disks
    if not free_disks:
      raise Exception('There are no unused flash drives to use as a read cache')

    if request.method == "GET":
      #Return the conf page

      initial = {}
      initial['pool'] = pool_name

      form = zfs_forms.L2arcForm(initial=initial, free_disks = free_disks)
      return_dict['form'] = form
      return django.shortcuts.render_to_response("edit_zfs_l2arc.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = zfs_forms.L2arcForm(request.POST, free_disks = free_disks)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("edit_zfs_l2arc.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      #print cd
      result, err = zfs.set_pool_cache_vdev(cd['pool'], cd['disk'])
      if err:
        raise Exception(err)
      ret, err = audit.audit("edit_zfs_l2arc", 'Changed the read cache for pool %s to a flash drive'%(cd['pool']), request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_pool?action=changed_l2arc&name=%s'%pool_name)
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Set ZFS pool read cache'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error setting ZFS pool read cache'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def remove_zfs_l2arc(request):

  return_dict = {}
  try:

    if 'pool' not in request.REQUEST:
      raise Exception("No pool specified. Please use the menus")

    if 'device' not in request.REQUEST:
      raise Exception("No device specified. Please use the menus")

    pool = request.REQUEST["pool"]
    return_dict["pool"] = pool

    device = request.REQUEST["device"]
    return_dict["device"] = device

    if request.method == "GET":
      #Return the conf page
      return django.shortcuts.render_to_response("remove_zfs_l2arc_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      result, err = zfs.remove_pool_vdev(pool, device)
      if not result:
        if not err:
          raise Exception('Unknown error!')
        else:
          raise Exception(err)
 
      audit_str = "Removed ZFS read cache for pool %s"%pool
      ret, err = audit.audit("remove_zfs_l2arc", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_pool?name=%s&action=l2arc_deleted'%pool)
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Removing ZFS pool read cache'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error removing ZFS pool read cache'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_zfs_dataset(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'

    if 'name' not in request.REQUEST :
      raise Exception("Malformed request. Please use the menus.")

    if "action" in request.GET:
      if request.GET["action"] == "set_quota":
        conf = "ZFS quota successfully set"
      elif request.GET["action"] == "removed_quota":
        conf = "ZFS quota successfully removed"
      elif request.GET["action"] == "set_permissions":
        conf = "Directory ownership/permissions successfully set"
      elif request.GET["action"] == "modified_dataset_properties":
        conf = "ZFS dataset/volume configuration successfully modified"
      elif request.GET["action"] == "created_dataset":
        conf = "ZFS dataset successfully created"
      if conf:
        return_dict["conf"] = conf
    
    dataset_name = request.REQUEST['name']
    if '/' in dataset_name:
      pos = dataset_name.find('/')
      pool = dataset_name[:pos]
    else:
      pool = dataset_name
    return_dict['pool'] = pool

    properties, err = zfs.get_properties(dataset_name)
    if err:
      raise Exception(err)
    elif not properties:
      raise Exception("Specified dataset not found")

    children, err = zfs.get_children_datasets(dataset_name)
    if err:
      raise Exception(err)

    quotas, err = zfs.get_all_quotas(dataset_name)
    if err:
      raise Exception(err)

    schedule, err = zfs.get_snapshot_schedule(dataset_name)
    if err:
      raise Exception(err)

    return_dict['snapshot_schedule'] = schedule

    if children:
      return_dict['children'] = children
    return_dict['name'] = dataset_name
    return_dict['properties'] = properties
    return_dict['quotas'] = quotas
    return_dict['exposed_properties'] = ['compression', 'compressratio', 'dedup',  'type', 'usedbychildren', 'usedbydataset', 'creation']
    if 'result' in request.GET:
      return_dict['result'] = request.GET['result']

    template = "view_zfs_dataset.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'ZFS dataset details'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error loading ZFS dataset details'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def edit_zfs_dataset(request):
  return_dict = {}
  try:
    if 'name' not in request.REQUEST:
      raise Exception('Dataset name not specified. Please use the menus.')
    name = request.REQUEST["name"]
    properties, err = zfs.get_properties(name)
    if not properties and err:
      raise Exception(err)
    elif not properties:
      raise Exception("Error loading ZFS dataset properties")

    if request.method == "GET":
      #Return the conf page
      initial = {}
      initial['name'] = name
      for p in ['compression', 'dedup', 'readonly']:
        if properties[p]['value'] == 'off':
          initial[p] = False
        else:
          initial[p] = True

      form = zfs_forms.DatasetForm(initial=initial)
      return_dict['form'] = form
      return django.shortcuts.render_to_response("edit_zfs_dataset.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = zfs_forms.DatasetForm(request.POST)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("edit_zfs_dataset.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      result_str = ""
      audit_str = "Changed the following dataset properties for dataset %s : "%name
      success = False
      # Do this for all boolean values
      to_change = []
      for p in ['compression', 'dedup', 'readonly']:
        orig = properties[p]['value']
        if cd[p]:
          changed = 'on'
        else:
          changed = 'off'
        #print 'property %s orig %s changed %s'%(p, orig, changed)
        if orig != changed:
          result, err = zfs.set_property(name, p, changed)
          #print err
          if not result:
            result_str += ' Error setting property %s'%p
            if not err:
              results += ' : %s'%str(e)
          else:
            result_str += ' Successfully set property %s to %s'%(p, changed)
            audit_str += " property '%s' set to '%s'"%(p, changed)
            success = True
      if success:
        audit.audit("edit_zfs_dataset", audit_str, request.META["REMOTE_ADDR"])
                
      #return django.http.HttpResponseRedirect('/view_zfs_dataset?name=%s&result=%s'%(name, result_str))
      return django.http.HttpResponseRedirect('/view_zfs_dataset?name=%s&action=modified_dataset_properties'%name)
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Modify ZFS dataset properties'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error modify ZFS dataset properties'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def delete_zfs_dataset(request):

  return_dict = {}
  try:
    if 'name' not in request.REQUEST:
      raise Exception("Error deleting ZFS dataset- No dataset specified. Please use the menus")
    if 'type' not in request.REQUEST:
      type = 'dataset'
    else:
      type = request.REQUEST['type']
    name = request.REQUEST["name"]
    pool_name = request.REQUEST["pool_name"]
    nfs_shares, err = nfs.get_shares_on_subpath('%s/'%name)
    if err:
      raise Exception(err)
    cifs_shares, err = common_cifs.get_shares_on_subpath('%s/'%name)
    if err:
      raise Exception(err)
    luns, err = iscsi_stgt.get_luns_on_subpath('%s/'%name)
    if err:
      raise Exception(err)
    if nfs_shares or cifs_shares or luns:
      elements = []
      if nfs_shares:
        shl=[]
        for sh in nfs_shares:
          shl.append(sh['path'])
        elements .append('NFS share(s) : %s'%' , '.join(shl))
      if cifs_shares:
        shl=[]
        for sh in cifs_shares:
          shl.append(sh['name'])
        elements .append('CIFS share(s) : %s'%' , '.join(shl))
      if luns:
        shl=[]
        for sh in luns:
          shl.append(sh['path'][9:])
        elements .append('ISCSI LUN(s) : %s'%' , '.join(shl))
      raise Exception('The dataset cannot be deleted as the following components exist on this pool : %s. Please delete them first before deleting the pool.'%' , '.join(elements))
    return_dict["name"] = name
    return_dict["pool_name"] = pool_name
    return_dict["type"] = type
    if request.method == "GET":
      #Return the conf page
      return django.shortcuts.render_to_response("delete_zfs_dataset_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      result, err = zfs.delete_dataset(name)
      if not result:
        if not err:
          raise Exception('Unknown error!')
        else:
          raise Exception(err)
 
      if type == 'dataset':
        audit_str = "Deleted ZFS dataset %s"%name
        audit.audit("delete_zfs_dataset", audit_str, request.META["REMOTE_ADDR"])
        return django.http.HttpResponseRedirect('/view_zfs_pool?action=dataset_deleted&name=%s'%pool_name)
      else:
        audit_str = "Deleted ZFS block device volume %s"%name
        audit.audit("delete_zfs_zvol", audit_str, request.META["REMOTE_ADDR"])
        return django.http.HttpResponseRedirect('/view_zfs_pool?action=zvol_deleted&name=%s'%pool_name)
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Remove a ZFS dataset/volume'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error removing a dataset/volume '
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_zfs_dataset(request):
  return_dict = {}
  try:
    if 'pool' not in request.REQUEST:
      raise Exception("No parent pool provided. Please use the menus.")
    pool = request.REQUEST['pool']
    datasets, err = zfs.get_children_datasets(pool)
    if err:
      raise Exception("Could not retrieve the list of existing datasets")
    if pool not in datasets:
      datasets.append(pool)
    return_dict['pool'] = pool

    if request.method == "GET":
      #Return the conf page
      initial = {}
      initial['pool'] = pool
      form = zfs_forms.CreateDatasetForm(initial=initial)
      return_dict['form'] = form
      return django.shortcuts.render_to_response("create_zfs_dataset.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = zfs_forms.CreateDatasetForm(request.POST)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("create_zfs_dataset.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      properties = {}
      if 'compression' in cd and cd['compression']:
        properties['compression'] = 'on'
      if 'dedup' in cd and cd['dedup']:
        properties['dedup'] = 'on'
      result, err = zfs.create_dataset(cd['pool'], cd['name'], properties)
      if not result:
        if not err:
          raise Exception('Unknown error!')
        else:
          raise Exception(err)
 
      audit_str = "Created a ZFS dataset named %s/%s"%(cd['pool'], cd['name'])
      audit.audit("create_zfs_dataset", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_pool?name=%s&action=created_dataset'%pool)
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Create a ZFS dataset'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error creating a ZFS dataset'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_zfs_zvol(request):
  return_dict = {}
  try:
    if 'pool' not in request.REQUEST:
      raise Exception("No parent pool provided. Please use the menus.")
    pool = request.REQUEST['pool']
    return_dict['pool'] = pool

    if request.method == "GET":
      parent = None
      if 'parent' in request.GET:
        parent = request.GET['parent']
      initial = {}
      initial['pool'] = pool
      initial['block_size'] = '64K'
      form = zfs_forms.CreateZvolForm(initial=initial)
      return_dict['form'] = form
      return django.shortcuts.render_to_response("create_zfs_zvol.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = zfs_forms.CreateZvolForm(request.POST)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("create_zfs_zvol.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      properties = {}
      if 'compression' in cd and cd['compression']:
        properties['compression'] = 'on'
      if 'dedup' in cd and cd['dedup']:
        properties['dedup'] = 'on'
      if 'thin_provisioned' in cd and cd['thin_provisioned']:
        thin = True
      else:
        thin = False
      result, err = zfs.create_zvol(cd['pool'], cd['name'], properties, cd['size'], cd['unit'], cd['block_size'], thin)
      if not result:
        if not err:
          raise Exception('Unknown error!')
        else:
          raise Exception(err)
 
      if thin:
        audit_str = "Created a thinly provisioned ZFS block device volume named %s/%s with size %s%s"%(cd['pool'], cd['name'], cd['size'],cd['unit'])
      else:
        audit_str = "Created a ZFS block device volume named %s/%s with size %s%s"%(cd['pool'], cd['name'], cd['size'],cd['unit'])
      audit.audit("create_zfs_zvol", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_pool?action=created_zvol&name=%s'%pool)
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Create a ZFS block device volume'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error creating a ZFS block device volume '
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_zfs_zvol(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'
    if 'name' not in request.REQUEST:
      raise Exception("No block device volume specified.")
    
    name = request.REQUEST['name']
    if '/' in name:
      pos = name.find('/')
      pool = name[:pos]
    else:
      pool = name
    return_dict['pool'] = pool

    properties, err = zfs.get_properties(name)
    if not properties and err:
      raise Exception(err)
    elif not properties:
      raise Exception("Specified block device volume not found")

    return_dict['name'] = name
    return_dict['properties'] = properties
    return_dict['exposed_properties'] = ['compression', 'compressratio', 'dedup',  'type',  'creation']
    if 'result' in request.GET:
      return_dict['result'] = request.GET['result']

    template = "view_zfs_zvol.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'ZFS block device volume details'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error loading ZFS block device volume details'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_zfs_snapshots(request):
  return_dict = {}
  try:

    datasets, err = zfs.get_all_datasets_and_pools()
    if err:
      raise Exception(err)

    #If the list of snapshots is for a particular dataset or pool, get the name of that ds or pool
    name = None
    snap_list = None
    initial = {}
    if 'name' in request.GET:
      name = request.GET['name']
    else:
      if datasets:
        name = datasets[0]
    if name:
      initial['name'] = name
      snap_list, err = zfs.get_snapshots(name)
      if err:
        raise Exception(err)

    if "action" in request.GET:
      conf = None
      if request.GET["action"] == "created":
        conf = "ZFS snapshot successfully created"
      elif request.GET["action"] == "deleted":
        conf = "ZFS snapshot successfully destroyed"
      elif request.GET["action"] == "scheduled":
        conf = "ZFS snapshot schedule successfully modified"
      elif request.GET["action"] == "renamed":
        conf = "ZFS snapshot successfully renamed"
      elif request.GET["action"] == "rolled_back":
        conf = "ZFS filesystem successfully rolled back to the snapshot"
      if conf:
        return_dict["conf"] = conf

    form = zfs_forms.ViewSnapshotsForm(initial = initial, datasets = datasets)
    return_dict['form'] = form
    return_dict["snap_list"] = snap_list
    template = "view_zfs_snapshots.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'ZFS snapshots'
    return_dict['tab'] = 'view_zfs_snapshots_tab'
    return_dict["error"] = 'Error loading ZFS snapshots'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_zfs_snapshot(request):
  return_dict = {}
  try:
    datasets, err = zfs.get_all_datasets_and_pools()
    if not datasets:
      raise Exception("Could not get the list of existing datasets")

    if request.method == "GET":
      target = None
      if 'target' in request.GET:
        target = request.GET['target']
      #Return the conf page
      initial = {}
      if target:
        initial['target'] = target
      form = zfs_forms.CreateSnapshotForm(initial=initial, datasets = datasets)
      return_dict['form'] = form
      return django.shortcuts.render_to_response("create_zfs_snapshot.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = zfs_forms.CreateSnapshotForm(request.POST, datasets = datasets)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("create_zfs_snapshot.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      '''
      if request.POST.get("id_scheduler"):
        target = cd['target']
        result, err = zfs.get_create_snapshot_command(target)
        if err:
          raise Exception(err)
        if result:
          # <QueryDict: {u'is_scheduler': [u'on'], u'target': [u'pool1'], u'is_week': [u''], u'is_hour': [u'', u''], u'is_month': [u'', u''], u'name': [u'snap1']}> /sbin/zfs snapshot pool1@snap1
          min = request.POST.get('id_minute')
          hour = request.POST.get('id_hour')
          day_of_month = request.POST.get('id_day_of_month')
          month = request.POST.get('id_month')
          week = request.POST.get('id_week')
          result = result + "$(date +\%d-\%m-\%Y-\%I-\%M)"
          msg,err = scheduler_utils.create_cron("ZFS Snapshot Creation",min,hour,day_of_month,month,week,result,None)
          if msg:
            return_dict["conf"] = "Snapshot Schedule Successful"
          else:
            return_dict["conf"] = "Snapshot Schedule Unsuccessful"
      else:
      '''
      result, err = zfs.create_snapshot(cd['target'], cd['name'])
      if not result:
        if not err:
          raise Exception('Unknown error!')
        else:
          raise Exception(err)
 
      audit_str = "Created a ZFS snapshot named %s for target %s"%(cd['name'], cd['target'])
      audit.audit("create_zfs_snapshot", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_snapshots?action=created')
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Create a ZFS snapshot'
    return_dict['tab'] = 'view_zfs_snapshots_tab'
    return_dict["error"] = 'Error creating a ZFS snapshot'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def delete_zfs_snapshot(request):

  return_dict = {}
  try:
    if 'name' not in request.REQUEST:
      raise Exception("No snapshot name specified. Please use the menus")
    name = request.REQUEST["name"]
    if 'display_name' in request.REQUEST:
      return_dict["display_name"] = request.REQUEST['display_name']
    return_dict["name"] = name

    if request.method == "GET":
      #Return the conf page
      return django.shortcuts.render_to_response("delete_zfs_snapshot_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      result, err = zfs.delete_snapshot(name)
      if not result:
        if not err:
          raise Exception('Unknown error!')
        else:
          raise Exception(err)
 
      audit_str = "Deleted ZFS snapshot %s"%name
      audit.audit("delete_zfs_snapshot", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_snapshots?action=deleted')
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Delete a ZFS snapshot'
    return_dict['tab'] = 'view_zfs_snapshots_tab'
    return_dict["error"] = 'Error deleting a ZFS snapshot'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def rollback_zfs_snapshot(request):

  return_dict = {}
  try:
    if 'name' not in request.REQUEST:
      raise Exceptio("No snapshot name specified. Please use the menus")
    name = request.REQUEST["name"]
    if 'display_name' in request.REQUEST:
      return_dict["display_name"] = request.REQUEST['display_name']
    return_dict["name"] = name

    if request.method == "GET":
      #Return the conf page
      return django.shortcuts.render_to_response("rollback_zfs_snapshot_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      result, err = zfs.rollback_snapshot(name)
      if not result:
        if not err:
          raise Exception('Unknown error!')
        else:
          raise Exception(err)
 
      audit_str = "Rolled back to ZFS snapshot %s"%name
      audit.audit("rollback_zfs_snapshot", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_snapshots?action=rolled_back')
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Rollback a ZFS snapshot'
    return_dict['tab'] = 'view_zfs_snapshots_tab'
    return_dict["error"] = 'Error rolling back a  ZFS snapshot'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def rename_zfs_snapshot(request):
  return_dict = {}
  try:
    if request.method == "GET":
      if ('ds_name' not in request.GET) or ('snapshot_name' not in request.GET):
        raise Exception("Required info not passed. Please use the menus.")

      ds_name = request.GET['ds_name']
      snapshot_name = request.GET['snapshot_name']
      #Return the conf page
      initial = {}
      initial['snapshot_name'] = snapshot_name
      initial['ds_name'] = ds_name
      form = zfs_forms.RenameSnapshotForm(initial=initial)
      return_dict['form'] = form
      return django.shortcuts.render_to_response("rename_zfs_snapshot.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = zfs_forms.RenameSnapshotForm(request.POST)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("rename_zfs_snapshot.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      result, err = zfs.rename_snapshot(cd['ds_name'], cd['snapshot_name'], cd['new_snapshot_name'])
      if not result:
        if not err:
          raise Exception('Unknown error!')
        else:
          raise Exception(err)
 
      audit_str = "Renamed  ZFS snapshot for %s from %s to %s"%(cd['ds_name'], cd['snapshot_name'], cd['new_snapshot_name'])
      audit.audit("rename_zfs_snapshot", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_snapshots?action=renamed')
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Rename a ZFS snapshot'
    return_dict['tab'] = 'view_zfs_snapshots_tab'
    return_dict["error"] = 'Error renaming a loading ZFS snapshot'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def schedule_zfs_snapshot(request):
  return_dict = {}
  try:
    datasets, err = zfs.get_all_datasets_and_pools()
    if err:
      raise Exception(err)
    if not datasets:
      raise Exception("Could not get the list of existing datasets")

    if request.method == "GET":
      target = None
      if 'target' in request.GET:
        target = request.GET['target']
      #Return the conf page
      schedule = None
      if not target:
        target = datasets[0]
      schedule, err = zfs.get_snapshot_schedule(target)
      if err:
        raise Exception(err)
      initial = {}
      if schedule:
        initial['frequent'] = schedule['frequent']
        initial['hourly'] = schedule['hourly']
        initial['daily'] = schedule['daily']
        initial['weekly'] = schedule['weekly']
        initial['monthly'] = schedule['monthly']
      if target:
        initial['target'] = target
      form = zfs_forms.ScheduleSnapshotForm(initial = initial, datasets = datasets)
      return_dict['form'] = form
      return django.shortcuts.render_to_response("schedule_zfs_snapshot.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = zfs_forms.ScheduleSnapshotForm(request.POST, datasets = datasets)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("create_zfs_snapshot.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      target = cd['target']
      frequent = cd['frequent']
      hourly = cd['hourly']
      daily = cd['daily']
      weekly = cd['weekly']
      monthly = cd['monthly']
      result, err = zfs.schedule_snapshot(target, frequent, hourly, daily, weekly, monthly)
      audit_str = "Enabled/Modified ZFS snapshot scheduling for target %s "%cd['target']
      if err:
        raise Exception(err)
 
      audit.audit("schedule_zfs_snapshot", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_snapshots?action=scheduled')
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Schedule a ZFS snapshot'
    return_dict['tab'] = 'view_zfs_snapshots_tab'
    return_dict["error"] = 'Error scheduling ZFS snapshot'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def add_zfs_spares(request):
  return_dict = {}
  try:
    if 'pool_name' not in request.REQUEST:
      raise Exception('No pool specified. Please use the menus')
    pool_name = request.REQUEST['pool_name']
    free_drives, err = zfs.get_free_disks_for_spares(pool_name)
    if err:
      raise Exception(err)
    num_free_drives = len(free_drives)
    if request.method == 'GET':
      if num_free_drives == 0:
        raise Exception('There are no free drives to be added as spares')
      form = zfs_forms.AddSparesForm(num_free_drives = num_free_drives)
      return_dict['form'] = form
      return_dict['pool_name'] = pool_name
      return django.shortcuts.render_to_response("add_zfs_spares.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = zfs_forms.AddSparesForm(request.POST, num_free_drives = num_free_drives)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("add_zfs_spares.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      num_spares = cd['num_spares']
      #print num_spares
      ret, err = zfs.add_spares_to_pool(pool_name, int(num_spares))
      if err:
        raise Exception(err)
      audit_str = "Added %s spare drive(s) to pool %s"%(num_spares, pool_name)
      audit.audit("add_zfs_spares", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_pool?action=added_spares&name=%s'%pool_name)
      
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Add spare drives to a ZFS pool'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error adding spares drives to a ZFS pool'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def remove_zfs_spare(request):
  return_dict = {}
  try:
    if 'pool_name' not in request.REQUEST:
      raise Exception('No pool specified. Please use the menus')
    pool_name = request.REQUEST['pool_name']
    spares, err = zfs.get_pool_spares(pool_name)
    if err:
      raise Exception(err)
    if not spares:
      raise Exception('The pool does not have any spare drives assigned to it')
    if request.method == 'GET':
      return_dict['pool_name'] = pool_name
      return django.shortcuts.render_to_response("remove_zfs_spare_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      ret, err = zfs.remove_a_spare_from_pool(pool_name)
      if err:
        raise Exception(err)
      audit_str = "Removed a  spare drive from pool %s"%pool_name
      audit.audit("remove_zfs_spare", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_pool?action=removed_spare&name=%s'%pool_name)
      
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Remove a spare disk from a ZFS pool'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error removing a  spares disk from a ZFS pool'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def replace_disk(request):

  return_dict = {}
  try:
    form = None
  
    si, err = system_info.load_system_config()
    if err:
      raise Exception(err)
    if not si:
      raise Exception('Error loading system config')

    return_dict['system_config_list'] = si
    
    template = 'logged_in_error.html'
    use_salt, err = common.use_salt()
    if err:
      raise Exception(err)
  
    if request.method == "GET":
      raise Exception("Incorrect access method. Please use the menus")
    else:
      if 'node' in request.POST:
        node = request.POST["node"]
      else:
        node = si.keys()[0]
      serial_number = request.POST["serial_number"]
  
      if "conf" in request.POST:
        if "node" not in request.POST or  "serial_number" not in request.POST:
          raise Exception("Incorrect access method. Please use the menus")
        elif request.POST["node"] not in si:
          raise Exception("Unknown node. Please use the menus")
        elif "step" not in request.POST :
          raise Exception("Incomplete request. Please use the menus")
        elif request.POST["step"] not in ["offline_disk", "scan_for_new_disk", "online_new_disk"]:
          raise Exception("Incomplete request. Please use the menus")
        else:
          step = request.POST["step"]
  
          # Which step of the replace disk are we in?
  
          if step == "offline_disk":
  
            #get the pool corresponding to the disk
            #zpool offline pool disk
            #send a screen asking them to replace the disk
  
            pool = None
            if serial_number in si[node]["disks"]:
              disk = si[node]["disks"][serial_number]
              if "pool" in disk:
                pool = disk["pool"]
              disk_id = disk["id"]
            if not pool:
              raise Exception("Could not find the storage pool on that disk. Please use the menus")
            else:
              cmd_to_run = 'zpool offline %s %s'%(pool, disk_id)
              #print 'Running %s'%cmd_to_run
              #assert False
              if use_salt:
                #issue a zpool offline pool disk-id using salt
                client = salt.client.LocalClient()
                rc = client.cmd(node, 'cmd.run_all', [cmd_to_run])
                if rc:
                  for node, ret in rc.items():
                    #print ret
                    if ret["retcode"] != 0:
                      error = "Error bringing the disk with serial number %s offline on %s : "%(serial_number, node)
                      if "stderr" in ret:
                        error += ret["stderr"]
                      raise Exception(error)
                #print rc
              else:
                (ret, rc), err = command.execute_with_rc(cmd_to_run)
                if err:
                  raise Exception(err)
                #print ret
                if rc != 0:
                  err = "Error bringing the disk with serial number %s offline  : "%(serial_number)
                  tl, er = command.get_output_list(ret)
                  if er:
                    raise Exception(er)
                  if tl:
                    err = ','.join(tl)
                  tl, er = command.get_error_list(ret)
                  if er:
                    raise Exception(er)
                  if tl:
                    err = err + ','.join(tl)
                  raise Exception(err)  
              #if disk_status == "Disk Missing":
              #  #Issue a reboot now, wait for a couple of seconds for it to shutdown and then redirect to the template to wait for reboot..
              #  pass
              audit_str = "Replace disk - Disk with serial number %s brought offline"%serial_number
              audit.audit("replace_disk_offline_disk", audit_str, request.META["REMOTE_ADDR"])
              return_dict["serial_number"] = serial_number
              return_dict["node"] = node
              return_dict["pool"] = pool
              return_dict["old_id"] = disk_id
              template = "replace_disk_prompt.html"
  
          elif step == "scan_for_new_disk":
  
            #they have replaced the disk so scan for the new disk
            # and prompt for a confirmation of the new disk serial number
  
            pool = request.POST["pool"]
            old_id = request.POST["old_id"]
            return_dict["node"] = node
            return_dict["serial_number"] = serial_number
            return_dict["pool"] = pool
            return_dict["old_id"] = old_id
            old_disks = si[node]["disks"].keys()
            result = False
            if use_salt:
              client = salt.client.LocalClient()
              rc = client.cmd(node, 'integralstor.disk_info_and_status')
              if rc and node in rc:
                result = True
                new_disks = rc[node]
            else:
              rc, err = manifest_status.disk_info_and_status()
              if err:
                raise Exception(err)
              if rc:
                result = True
                new_disks = rc
            if result:
              #print '1'
              if new_disks:
                #print new_disks.keys()
                #print old_disks
                for disk in new_disks.keys():
                  #print disk
                  if disk not in old_disks:
                    #print '3'
                    return_dict["inserted_disk_serial_number"] = disk
                    return_dict["new_id"] = new_disks[disk]["id"]
                    break
                if "inserted_disk_serial_number" not in return_dict:
                  raise Exception("Could not detect any new disk. Please check the new disk is inserted and give the system a few seconds to detect the drive and refresh the page to try again.")
                else:
                  template = "replace_disk_confirm_new_disk.html"
          elif step == "online_new_disk":
  
            pool = request.POST["pool"]
            old_id = request.POST["old_id"]
            new_id = request.POST["new_id"]
            new_serial_number = request.POST["new_serial_number"]
            db_path, err = common.get_db_path()
            if err:
              raise Exception(err)
            common_python_scripts_path, err = common.get_common_python_scripts_path()
            if err:
              raise Exception(err)
            cmd_list = []
            cmd_list.append({'Replace old disk':'zpool replace -f %s %s %s'%(pool, old_id, new_id)})
            cmd_list.append({'Online the new disk':'zpool online %s %s'%(pool, new_id)})
            cmd_list.append({'Regenerate the system configuration':'%s/generate_manifest.py'%common_python_scripts_path})
            ret, err = scheduler_utils.schedule_a_job(db_path,'Disk replacement',cmd_list,None,retries=0)
            if err:
              raise Exception(err)
            if not ret:
              raise Exception('Error scheduling disk replacement tasks')
            audit_str = "Replace disk - Scheduled a task for replacing the old disk with serial number %s with the new disk with serial number %s"%(serial_number, new_serial_number)
            audit.audit("replace_disk_replaced_disk", audit_str, request.META["REMOTE_ADDR"])
            return_dict["node"] = node
            return_dict["old_serial_number"] = serial_number
            return_dict["new_serial_number"] = new_serial_number
            template = "replace_disk_success.html"
            '''
            python_scripts_path, err = common.get_python_scripts_path()
            if err:
              raise Exception(err)
            common_python_scripts_path, err = common.get_common_python_scripts_path()
            if err:
              raise Exception(err)
            #they have confirmed the new disk serial number
            #get the id of the disk and
            #zpool replace poolname old disk new disk
            #zpool clear poolname to clear old errors
            #return a result screen
            pool = request.POST["pool"]
            old_id = request.POST["old_id"]
            new_id = request.POST["new_id"]
            new_serial_number = request.POST["new_serial_number"]
            cmd_to_run = "zpool replace -f %s %s %s"%(pool, old_id, new_id)
            if use_salt:
              #print 'Running %s'%cmd_to_run
              client = salt.client.LocalClient()
              rc = client.cmd(node, 'cmd.run_all', [cmd_to_run])
              if rc:
                #print rc
                for node, ret in rc.items():
                  #print ret
                  if ret["retcode"] != 0:
                    error = "Error replacing the disk on %s : "%(node)
                    if "stderr" in ret:
                      error += ret["stderr"]
                    rc = client.cmd(node, 'cmd.run', ['zpool online %s %s'%(pool, old_id)])
                    raise Exception(error) 
              else:
                raise Exception("Error replacing the disk on %s : "%(node))
            else:
                (ret, rc), err = command.execute_with_rc(cmd_to_run)
                if err:
                  raise Exception(err)
                #print ret
                if rc != 0:
                  err = "Error replacing the disk  : "
                  tl, er = command.get_output_list(ret)
                  if er:
                    raise Exception(er)
                  if tl:
                    err = ','.join(tl)
                  tl, er = command.get_error_list(ret)
                  if er:
                    raise Exception(er)
                  if tl:
                    err = err + ','.join(tl)
                  raise Exception(err)
            '''
            '''
            cmd_to_run = "zpool set autoexpand=on %s"%pool
            if use_salt:
              print 'Running %s'%cmd_to_run
              rc = client.cmd(node, 'cmd.run_all', [cmd_to_run])
              if rc:
                for node, ret in rc.items():
                  #print ret
                  if ret["retcode"] != 0:
                    error = "Error setting pool autoexpand on %s : "%(node)
                    if "stderr" in ret:
                      error += ret["stderr"]
                    return_dict["error"] = error
                    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
              print rc
            else:
              (ret, rc), err = command.execute_with_rc(cmd_to_run)
              if err:
                raise Exception(err)
              #print ret
              if rc != 0:
                err = "Error setting pool autoexpand on %s : "%(node)
                tl, er = command.get_output_list(ret)
                if er:
                  raise Exception(er)
                if tl:
                  err = ','.join(tl)
                tl, er = command.get_error_list(ret)
                if er:
                  raise Exception(er)
                if tl:
                  err = err + ','.join(tl)
                return_dict["error"] = err
                return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
            if new_serial_number in si[node]["disks"]:
              disk = si[node]["disks"][new_serial_number]
              disk_id = disk["id"]
            '''
            '''
            cmd_to_run = 'zpool online %s %s'%(pool, new_id)
            if use_salt:
              #print 'Running %s'%cmd_to_run
              rc = client.cmd(node, 'cmd.run_all', [cmd_to_run])
              if rc:
                #print rc
                for node, ret in rc.items():
                  #print ret
                  if ret["retcode"] != 0:
                    error = "Error bringing the new disk online on %s : "%(node)
                    if "stderr" in ret:
                      error += ret["stderr"]
                    raise Exception(error)
              else:
                raise Exception("Error bringing the new disk online on %s : "%(node))
            else:
              (ret, rc), err = command.execute_with_rc(cmd_to_run)
              if err:
                raise Exception(err)
              #print ret
              if rc != 0:
                err = "Error bringing the new disk online  : "
                tl, er = command.get_output_list(ret)
                if er:
                  raise Exception(er)
                if tl:
                  err = ','.join(tl)
                tl, er = command.get_error_list(ret)
                if er:
                  raise Exception(er)
                if tl:
                  err = err + ','.join(tl)
                raise Exception(err)
            (ret, rc), err = command.execute_with_rc('%s/generate_manifest.py'%common_python_scripts_path)
            if err:
              raise Exception(err)
            #print ret
            if rc != 0:
              err = ""
              tl, er = command.get_output_list(ret)
              if er:
                raise Exception(er)
              if tl:
                err = ','.join(tl)
              tl, er = command.get_error_list(ret)
              if er:
                raise Exception(er)
              if tl:
                err = err + ','.join(tl)
              raise Exception("Could not regenrate the new hardware configuration. Error generating manifest. %s"%err)
              #print ret
            else:
              (ret, rc), err = command.execute_with_rc('%s/generate_status.py'%common_python_scripts_path)
              if err:
                raise Exception(err)
              if rc != 0:
                err = ""
                tl, er = command.get_output_list(ret)
                if er:
                  raise Exception(er)
                if tl:
                  err = ','.join(tl)
                tl, er = command.get_error_list(ret)
                if er:
                  raise Exception(er)
                if tl:
                  err = err + ','.join(tl)
                raise Exception("Could not regenrate the new hardware configuration. Error generating status. %s"%err)
                #print ret
              si, err = system_info.load_system_config()
              if err:
                raise Exception(err)
              audit_str = "Replace disk - Disk with serial number %s successfully replaced by new disk with serial number %s"%(serial_number, new_serial_number)
              audit.audit("replace_disk_replaced_disk", audit_str, request.META["REMOTE_ADDR"])
              return_dict["node"] = node
              return_dict["old_serial_number"] = serial_number
              return_dict["new_serial_number"] = new_serial_number
              template = "replace_disk_success.html"
  
          '''
          return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
          
      else:
        if "serial_number" not in request.POST:
          raise Exception("Incorrect access method. Please use the menus")
        else:
          if 'node' in request.POST:
            return_dict["node"] = request.POST["node"]
          else:
            node = si.keys()[0]
          return_dict["serial_number"] = request.POST["serial_number"]
          template = "replace_disk_conf.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "dashboard_base.html"
    return_dict["page_title"] = 'Replace a hard drive'
    return_dict['tab'] = 'disks_tab'
    return_dict["error"] = 'Error replacing hard drive'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def modify_dir_permissions(request):
  return_dict = {}
  try:
    if 'path' not in request.REQUEST:
      path = "/"
      #raise Exception('Path not specified')
    else:
      path = request.REQUEST['path']
    users, err = local_users.get_local_users()
    if err:
      raise Exception('Error retrieving local user list : %s'%err)
    if not users:
      raise Exception('No local users seem to be created. Please create at least one local user before performing this operation.')

    groups, err = local_users.get_local_groups()
    if err:
      raise Exception('Error retrieving local group list : %s'%err)
    if not groups:
      raise Exception('No local groups seem to be created. Please create at least one local group before performing this operation.')

    try:
      stat_info = os.stat(path)
    except Exception, e:
      raise Exception('Error accessing specified path : %s'%str(e))
    uid = stat_info.st_uid
    gid = stat_info.st_gid
    username = pwd.getpwuid(uid)[0]
    grpname = grp.getgrgid(gid)[0]
    return_dict["username"] = username
    return_dict["grpname"] = grpname
    pools, err = zfs.get_pools()
    ds_list = [] 
    for pool in pools:
      for ds in pool["datasets"]:
        if ds['properties']['type']['value'] == 'filesystem':
          ds_list.append(ds["name"])
    if not ds_list:
      raise Exception('No ZFS datasets available. Please create a dataset before creating shares.')
    return_dict["dataset"] = ds_list
    if request.method == "GET":
      # Shd be an edit request
  
      # Set initial form values
      initial = {}
      initial['path'] = path
      initial['owner_read'] = _owner_readable(stat_info)
      initial['owner_write'] = _owner_writeable(stat_info)
      initial['owner_execute'] = _owner_executeable(stat_info)
      initial['group_read'] = _group_readable(stat_info)
      initial['group_write'] = _group_writeable(stat_info)
      initial['group_execute'] = _group_executeable(stat_info)
      initial['other_read'] = _other_readable(stat_info)
      initial['other_write'] = _other_writeable(stat_info)
      initial['other_execute'] = _other_executeable(stat_info)
  
      form = common_forms.SetFileOwnerAndPermissionsForm(initial = initial, user_list = users, group_list = groups)
  
      return_dict["form"] = form
      return django.shortcuts.render_to_response('modify_dir_permissions.html', return_dict, context_instance=django.template.context.RequestContext(request))
  
    else:
      # Shd be an save request
      form = common_forms.SetFileOwnerAndPermissionsForm(request.POST, user_list = users, group_list = groups)
      return_dict["form"] = form
      if form.is_valid():
        cd = form.cleaned_data
        ret, err = file_processing.set_dir_ownership_and_permissions(cd)
        if not ret:
          if err:
            raise Exception(err)
          else:
            raise Exception("Error setting directory ownership/permissions.")
  
        audit_str = "Modified directory ownsership/permissions for %s"%cd["path"]
        audit.audit("modify_dir_owner_permissions", audit_str, request.META["REMOTE_ADDR"])
  
        return django.http.HttpResponseRedirect('/view_zfs_pools?action=set_permissions')
  
      else:
        #Invalid form
        return django.shortcuts.render_to_response('modify_dir_permissions.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Modify ownership/permissions on a directory'
    return_dict['tab'] = 'dir_permissions_tab'
    return_dict["error"] = 'Error modifying directory ownership/permissions'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def _owner_readable(st):
  return bool(st.st_mode & stat.S_IRUSR)
def _owner_writeable(st):
  return bool(st.st_mode & stat.S_IWUSR)
def _owner_executeable(st):
  return bool(st.st_mode & stat.S_IXUSR)

def _group_readable(st):
  return bool(st.st_mode & stat.S_IRGRP)
def _group_writeable(st):
  return bool(st.st_mode & stat.S_IWGRP)
def _group_executeable(st):
  return bool(st.st_mode & stat.S_IXGRP)

def _other_readable(st):
  return bool(st.st_mode & stat.S_IROTH)
def _other_writeable(st):
  return bool(st.st_mode & stat.S_IWOTH)
def _other_executeable(st):
  return bool(st.st_mode & stat.S_IXOTH)
