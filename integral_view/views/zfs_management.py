import django, django.template

import integralstor_common
import integralstor_unicell
from integralstor_common import zfs, audit, ramdisk
from integralstor_unicell import nfs

import integral_view
from integral_view.forms import zfs_forms
  
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
        elif request.GET["action"] == "created_pool":
          conf = "ZFS pool successfully created"
        elif request.GET["action"] == "set_permissions":
          conf = "Directory ownership/permissions successfully set"
        elif request.GET["action"] == "created_dataset":
          conf = "ZFS dataset successfully created"
        elif request.GET["action"] == "pool_deleted":
          conf = "ZFS pool successfully destroyed"
        elif request.GET["action"] == "dataset_deleted":
          conf = "ZFS dataset successfully destroyed"
        elif request.GET["action"] == "changed_slog":
          conf = "ZFS pool write cache successfully set"
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
    print pool.keys()

    if not pool and err:
      return_dict["error"] = "Error loading ZFS storage information : %s"%err
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
    elif not pool:
      return_dict["error"] = "Error loading ZFS storage information : Specified pool not found"
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))

    snap_list, err = zfs.get_snapshots(pool_name)
    if not snap_list and err:
      return_dict["error"] = "Error loading ZFS pool's snapshot  information : %s"%err
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
    return_dict['snap_list'] = snap_list
    

    return_dict['pool'] = pool
      
    template = "view_zfs_pool.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_zfs_pool(request):
  return_dict = {}
  try:
    free_disks, err = zfs.get_free_disks()
    if err:
      return_dict["error"] = "Error retrieving free disk information: %s"%err
      return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
    if not free_disks or len(free_disks) < 2:
      return_dict["error"] = "There are insufficient unused disks available to create a pool: %s"%err
      return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
    pool_types = []
    if len(free_disks) >= 2 :
      pool_types.append('mirror')
    if len(free_disks) >= 3 :
      pool_types.append('raid5')
    if len(free_disks) >= 4 :
      pool_types.append('raid6')
    if len(free_disks) >= 6 :
      pool_types.append('raid10')

    if request.method == "GET":
      #Return the conf page
      form = zfs_forms.CreatePoolForm(pool_types = pool_types, initial={'num_disks': len(free_disks)})
      return_dict['form'] = form
      return_dict['num_disks'] = len(free_disks)
      return django.shortcuts.render_to_response("create_zfs_pool.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = zfs_forms.CreatePoolForm(request.POST, pool_types = pool_types)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("create_zfs_pool.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      try :

        vdev_list = None
        if cd['pool_type'] in ['raid5', 'raid6']:
          vdev_list, err = zfs.create_pool_data_vdev_list(cd['pool_type'], cd['num_raid_disks'])
        elif cd['pool_type'] == 'raid10':
          vdev_list, err = zfs.create_pool_data_vdev_list(cd['pool_type'], cd['num_raid_disks'], cd['stripe_width'])
        else:
          vdev_list, err = zfs.create_pool_data_vdev_list(cd['pool_type'])
        if err:
          raise Exception(err)
        print 'vdevlist', vdev_list
        result, err = zfs.create_pool(cd['name'], cd['pool_type'], vdev_list)
        if not result:
          if not err:
            raise Exception('Unknown error!')
          else:
            raise Exception(err)
      except Exception, e:
        return_dict["error"] = "Error creating ZFS pool - %s"%str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
 
      audit_str = "Created a ZFS pool named %s of type %s"%(cd['name'], cd['pool_type'])
      audit.audit("create_zfs_pool", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_pools?action=created_pool')
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def delete_zfs_pool(request):

  return_dict = {}
  try:
    if 'name' not in request.REQUEST:
      return_dict["error"] = "Error deleting ZFS pool- No pool specified. Please use the menus"%str(e)
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    name = request.REQUEST["name"]
    return_dict["name"] = name
    if request.method == "GET":
      #Return the conf page
      return django.shortcuts.render_to_response("delete_zfs_pool_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      try :
        result, err = zfs.delete_pool(name)
        if not result:
          if not err:
            raise Exception('Unknown error!')
          else:
            raise Exception(err)
      except Exception, e:
        return_dict["error"] = "Error deleting ZFS pool- %s"%str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
 
      audit_str = "Deleted ZFS pool %s"%name
      audit.audit("delete_zfs_pool", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_pools?action=pool_deleted')
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def set_zfs_slog(request):
  return_dict = {}
  try:
    
    template = 'logged_in_error.html'

    if 'pool' not in request.REQUEST:
      return_dict["error"] = "Error loading ZFS pool information : No pool specified."
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))

    pool_name = request.REQUEST["pool"]

    pool, err = zfs.get_pool(pool_name)

    if not pool and err:
      return_dict["error"] = "Error loading ZFS storage information : %s"%err
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
    elif not pool:
      return_dict["error"] = "Error loading ZFS storage information : Specified pool not found"
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))

    slog = None
    if not pool['config']['logs']:
      slog = None
    else:
      kids = pool['config']['logs']['components']['logs']['children']
      if len(kids) == 1 and 'ramdisk' in kids[0]:
        slog = 'ramdisk'
        rdisk, err = ramdisk.get_ramdisk_info(pool_name)
        if err:
          return_dict["error"] = "Error loading ZFS pool RAM disk information : %s"%err
          return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
        elif not rdisk:
          return_dict["error"] = "Could not determine the configuration for the RAM disk for the specified ZFS pool "
          return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
        ramdisk_size = rdisk['size']/1024
      else:
        #For now pass but we need to code this to read the component disk ID!!!!!!!!!!!!1
        slog = 'ssd'
        pass

    if request.method == "GET":
      #Return the conf page


      initial = {}
      initial['pool'] = pool_name
      initial['slog'] = slog
      if slog == 'ramdisk':
        initial['ramdisk_size'] = ramdisk_size

      form = zfs_forms.SlogForm(initial=initial)
      return_dict['form'] = form
      return django.shortcuts.render_to_response("edit_zfs_slog.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = zfs_forms.SlogForm(request.POST)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("edit_zfs_slog.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      try :
        print cd
        if cd['slog'] == 'ramdisk':
          if ((cd['slog'] == slog) and (cd['ramdisk_size'] != ramdisk_size)) or (cd['slog'] != slog):
            # Changed to ramdisk or ramdisk parameters changed so destroy and recreate
            oldramdisk, err = ramdisk.get_ramdisk_info(cd['pool'])
            if oldramdisk:
              result, err = ramdisk.destroy_ramdisk(cd['pool'])
              if not result:
                return_dict["error"] = "Error destroying the current RAM disk for the specified ZFS pool : %s"%err
                return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
              result, err = zfs.remove_pool_vdev(cd['pool'], '/mnt/ramdisk_%s/ramfile'%cd['pool'])
              if not result:
                return_dict["error"] = "Error removing the current RAM disk from the specified ZFS pool : %s"%err
                return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
            result, err = ramdisk.create_ramdisk(1024*cd['ramdisk_size'], cd['pool'])
            if not result:
              return_dict["error"] = "Error creating the RAM disk for the specified ZFS pool : %s"%err
              return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
            else:
              result, err = zfs.set_pool_log_vdev(cd['pool'], '/mnt/ramdisk_%s/ramfile'%cd['pool'])
              if not result:
                ramdisk.destroy_ramdisk(cd['pool'])
                return_dict["error"] = "Error assigning the RAM disk to the specified ZFS pool : %s"%err
                return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
              audit.audit("edit_zfs_slog", 'Changed the write log for pool %s to a RAM disk of size %dGB'%(cd['pool'], cd['ramdisk_size']), request.META["REMOTE_ADDR"])
                
      except Exception, e:
        return_dict["error"] = "Error setting ZFS pool write cache - %s"%str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
 
      return django.http.HttpResponseRedirect('/view_zfs_pools?action=changed_slog')
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_zfs_dataset(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'
    if 'name' not in request.REQUEST:
      return_dict["error"] = "Error loading ZFS dataset information : No dataset specified."
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
    
    dataset_name = request.REQUEST['name']
    if '/' in dataset_name:
      pos = dataset_name.find('/')
      pool = dataset_name[:pos]
    else:
      pool = dataset_name
    return_dict['pool'] = pool

    properties, err = zfs.get_properties(dataset_name)
    if not properties and err:
      return_dict["error"] = "Error loading ZFS storage information : %s"%err
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
    elif not properties:
      return_dict["error"] = "Error loading ZFS storage information : Specified dataset not found"
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))

    children, err = zfs.get_children_datasets(dataset_name)
    if not children and err:
      return_dict["error"] = "Error loading ZFS children datasets: %s"%err
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))

    if children:
      return_dict['children'] = children
    return_dict['name'] = dataset_name
    return_dict['properties'] = properties
    return_dict['exposed_properties'] = ['compression', 'compressratio', 'dedup',  'type', 'usedbychildren', 'usedbydataset', 'creation']
    if 'result' in request.GET:
      return_dict['result'] = request.GET['result']

    template = "view_zfs_dataset.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def edit_zfs_dataset(request):
  return_dict = {}
  try:
    name = request.REQUEST["name"]
    properties, err = zfs.get_properties(name)
    if not properties and err:
      raise Exception("Error loading ZFS dataset properties : %s"%err)
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
    elif not properties:
      raise Exception("Error loading ZFS dataset properties")

    if request.method == "GET":
      #Return the conf page
      if 'name' not in request.GET:
        raise Exception('Dataset name not specified. Please use the menus. : %s'%err)


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
      try :
        # Do this for all boolean values
        to_change = []
        for p in ['compression', 'dedup', 'readonly']:
          orig = properties[p]['value']
          if cd[p]:
            changed = 'on'
          else:
            changed = 'off'
          print 'property %s orig %s changed %s'%(p, orig, changed)
          if orig != changed:
            result, err = zfs.set_property(name, p, changed)
            print err
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
                
      except Exception, e:
        return_dict["error"] = "Error saving ZFS dataset information - %s"%str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
 
      return django.http.HttpResponseRedirect('/view_zfs_dataset?name=%s&result=%s'%(name, result_str))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def delete_zfs_dataset(request):

  return_dict = {}
  try:
    if 'name' not in request.REQUEST:
      return_dict["error"] = "Error deleting ZFS dataset- No dataset specified. Please use the menus"%str(e)
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    name = request.REQUEST["name"]
    return_dict["name"] = name
    if request.method == "GET":
      #Return the conf page
      return django.shortcuts.render_to_response("delete_zfs_dataset_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      try :
        result, err = zfs.delete_dataset(name)
        if not result:
          if not err:
            raise Exception('Unknown error!')
          else:
            raise Exception(err)
      except Exception, e:
        return_dict["error"] = "Error deleting ZFS dataset- %s"%str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
 
      audit_str = "Deleted ZFS dataset %s"%name
      audit.audit("delete_zfs_dataset", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_pools?action=dataset_deleted')
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_zfs_dataset(request):
  return_dict = {}
  try:
    if 'pool' not in request.REQUEST:
      return_dict["error"] = "Error creating dataset - no parent pool provided. Please use the menus."
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    pool = request.REQUEST['pool']
    datasets, err = zfs.get_children_datasets(pool)
    if not datasets and err:
      raise Exception("Could not get the list of existing datasets")
    if pool not in datasets:
      datasets.append(pool)
    return_dict['pool'] = pool

    if request.method == "GET":
      parent = None
      if 'parent' in request.GET:
        parent = request.GET['parent']
      #Return the conf page
      initial = {}
      if parent:
        initial['parent'] = parent
      initial['pool'] = pool
      form = zfs_forms.CreateDatasetForm(initial=initial, datasets = datasets)
      return_dict['form'] = form
      return django.shortcuts.render_to_response("create_zfs_dataset.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = zfs_forms.CreateDatasetForm(request.POST, datasets = datasets)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("create_zfs_dataset.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      try :
        properties = {}
        if 'compression' in cd and cd['compression']:
          properties['compression'] = 'on'
        if 'dedup' in cd and cd['dedup']:
          properties['dedup'] = 'on'
        result, err = zfs.create_dataset(cd['parent'], cd['name'], properties)
        if not result:
          if not err:
            raise Exception('Unknown error!')
          else:
            raise Exception(err)
      except Exception, e:
        return_dict["error"] = "Error creating ZFS dataset - %s"%str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
 
      audit_str = "Created a ZFS dataset named %s/%s"%(cd['parent'], cd['name'])
      audit.audit("create_zfs_dataset", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_pools?action=created_dataset')
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_zfs_snapshots(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'

    #If the list of snapshots is for a particular dataset or pool, get the name of that ds or pool
    name = None
    if 'name' in request.GET:
      name = request.GET['name']

    snap_list, err = zfs.get_snapshots(name)
    if not snap_list and err:
      return_dict["error"] = "Error loading ZFS storage snapshot information : %s"%err
  
    if not "error" in return_dict:
      if "action" in request.GET:
        conf = None
        if request.GET["action"] == "created":
          conf = "ZFS snapshot successfully created"
        elif request.GET["action"] == "deleted":
          conf = "ZFS snapshot successfully destroyed"
        elif request.GET["action"] == "renamed":
          conf = "ZFS snapshot successfully renamed"
        elif request.GET["action"] == "rolled_back":
          conf = "ZFS filesystem successfully rolled back to the snapshot"
        if conf:
          return_dict["conf"] = conf
      return_dict["snap_list"] = snap_list
      template = "view_zfs_snapshots.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
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
      try :
        result, err = zfs.create_snapshot(cd['target'], cd['name'])
        if not result:
          if not err:
            raise Exception('Unknown error!')
          else:
            raise Exception(err)
      except Exception, e:
        return_dict["error"] = "Error creating ZFS snapshot - %s"%str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
 
      audit_str = "Created a ZFS snapshot named %s for target %s"%(cd['name'], cd['target'])
      audit.audit("create_zfs_snapshot", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_snapshots?action=created')
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def delete_zfs_snapshot(request):

  return_dict = {}
  try:
    if 'name' not in request.REQUEST:
      return_dict["error"] = "Error deleting ZFS snapshot- No snapshot name specified. Please use the menus"%str(e)
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    name = request.REQUEST["name"]
    if 'display_name' in request.REQUEST:
      return_dict["display_name"] = request.REQUEST['display_name']
    return_dict["name"] = name

    if request.method == "GET":
      #Return the conf page
      return django.shortcuts.render_to_response("delete_zfs_snapshot_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      try :
        result, err = zfs.delete_snapshot(name)
        if not result:
          if not err:
            raise Exception('Unknown error!')
          else:
            raise Exception(err)
      except Exception, e:
        return_dict["error"] = "Error deleting ZFS snapshot- %s"%str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
 
      audit_str = "Deleted ZFS snapshot %s"%name
      audit.audit("delete_zfs_snapshot", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_snapshots?action=deleted')
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def rollback_zfs_snapshot(request):

  return_dict = {}
  try:
    if 'name' not in request.REQUEST:
      return_dict["error"] = "Error rolling back to ZFS snapshot- No snapshot name specified. Please use the menus"%str(e)
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    name = request.REQUEST["name"]
    if 'display_name' in request.REQUEST:
      return_dict["display_name"] = request.REQUEST['display_name']
    return_dict["name"] = name

    if request.method == "GET":
      #Return the conf page
      return django.shortcuts.render_to_response("rollback_zfs_snapshot_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      try :
        result, err = zfs.rollback_snapshot(name)
        if not result:
          if not err:
            raise Exception('Unknown error!')
          else:
            raise Exception(err)
      except Exception, e:
        return_dict["error"] = "Error rolling back to ZFS snapshot- %s"%str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
 
      audit_str = "Rolled back to ZFS snapshot %s"%name
      audit.audit("rollback_zfs_snapshot", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_snapshots?action=rolled_back')
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def rename_zfs_snapshot(request):
  return_dict = {}
  try:
    if request.method == "GET":
      if ('ds_name' not in request.GET) or ('snapshot_name' not in request.GET):
        return_dict["error"] = "Error renaming ZFS snapshot - Required info not passed. Please use the menus."
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

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
      try :
        result, err = zfs.rename_snapshot(cd['ds_name'], cd['snapshot_name'], cd['new_snapshot_name'])
        if not result:
          if not err:
            raise Exception('Unknown error!')
          else:
            raise Exception(err)
      except Exception, e:
        return_dict["error"] = "Error renaming ZFS snapshot - %s"%str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
 
      audit_str = "Renamed  ZFS snapshot for %s from %s to %s"%(cd['ds_name'], cd['snapshot_name'], cd['new_snapshot_name'])
      audit.audit("rename_zfs_snapshot", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_zfs_snapshots?action=renamed')
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def replace_disk(request):

  return_dict = {}
  try:
    form = None
  
    si = system_info.load_system_config()
    return_dict['system_config_list'] = si
    
    template = 'logged_in_error.html'
  
    if request.method == "GET":
      return_dict["error"] = "Incorrect access method. Please use the menus"
    else:
      if 'node' in request.POST:
        node = request.POST["node"]
      else:
        node = si.keys()[0]
      serial_number = request.POST["serial_number"]
  
      if "error" in return_dict:
        return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  
      if "conf" in request.POST:
        if "node" not in request.POST or  "serial_number" not in request.POST:
          return_dict["error"] = "Incorrect access method. Please use the menus"
        elif request.POST["node"] not in si:
          return_dict["error"] = "Unknown GRIDCell. Please use the menus"
        elif "step" not in request.POST :
          return_dict["error"] = "Incomplete request. Please use the menus"
        elif request.POST["step"] not in ["offline_disk", "scan_for_new_disk", "online_new_disk"]:
          return_dict["error"] = "Incomplete request. Please use the menus"
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
              return_dict["error"] = "Could not find the storage pool on that disk. Please use the menus"
            else:
              #issue a zpool offline pool disk-id using salt
              client = salt.client.LocalClient()
              cmd_to_run = 'zpool offline %s %s'%(pool, disk_id)
              print 'Running %s'%cmd_to_run
              #assert False
              rc = client.cmd(node, 'cmd.run_all', [cmd_to_run])
              if rc:
                for node, ret in rc.items():
                  #print ret
                  if ret["retcode"] != 0:
                    error = "Error bringing the disk with serial number %s offline on %s : "%(serial_number, node)
                    if "stderr" in ret:
                      error += ret["stderr"]
                    return_dict["error"] = error
                    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
              print rc
              #if disk_status == "Disk Missing":
              #  #Issue a reboot now, wait for a couple of seconds for it to shutdown and then redirect to the template to wait for reboot..
              #  pass
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
            client = salt.client.LocalClient()
            rc = client.cmd(node, 'integralstor.disk_info_and_status')
            if rc and node in rc:
              new_disks = rc[node].keys()
              if new_disks:
                for disk in new_disks:
                  if disk not in old_disks:
                    return_dict["inserted_disk_serial_number"] = disk
                    return_dict["new_id"] = rc[node][disk]["id"]
                    break
                if "inserted_disk_serial_number" not in return_dict:
                  return_dict["error"] = "Could not detect any new disk."
                else:
                  template = "replace_disk_confirm_new_disk.html"
  
  
          elif step == "online_new_disk":
  
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
            print 'Running %s'%cmd_to_run
            client = salt.client.LocalClient()
            rc = client.cmd(node, 'cmd.run_all', [cmd_to_run])
            if rc:
              print rc
              for node, ret in rc.items():
                #print ret
                if ret["retcode"] != 0:
                  error = "Error replacing the disk on %s : "%(node)
                  if "stderr" in ret:
                    error += ret["stderr"]
                  rc = client.cmd(node, 'cmd.run', ['zpool online %s %s'%(pool, old_id)])
                  return_dict["error"] = error
                  return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
            else:
              error = "Error replacing the disk on %s : "%(node)
              return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
            '''
            cmd_to_run = "zpool set autoexpand=on %s"%pool
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
            if new_serial_number in si[node]["disks"]:
              disk = si[node]["disks"][new_serial_number]
              disk_id = disk["id"]
            '''
            cmd_to_run = 'zpool online %s %s'%(pool, new_id)
            print 'Running %s'%cmd_to_run
            rc = client.cmd(node, 'cmd.run_all', [cmd_to_run])
            if rc:
              print rc
              for node, ret in rc.items():
                #print ret
                if ret["retcode"] != 0:
                  error = "Error bringing the new disk online on %s : "%(node)
                  if "stderr" in ret:
                    error += ret["stderr"]
                  return_dict["error"] = error
                  return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
            else:
              error = "Error bringing the new disk online on %s : "%(node)
              return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
            ret, rc = integralstor_common.common.command.execute_with_rc('%s/generate_manifest.py'%integralstor_common.common.get_python_scripts_path())
            #print ret
            if rc != 0:
              return_dict["error"] = "Could not regenrate the new hardware configuration. Error generating manifest. Return code %d"%rc
              print ret
              return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
            else:
              ret, rc = integralstor_common.common.command.execute_with_rc('%s/generate_status.py'%integralstor_common.common.get_python_scripts_path())
              if rc != 0:
                print ret
                return_dict["error"] = "Could not regenrate the new hardware configuration. Error generating status. Return code %d"%rc
                return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
              si = system_info.load_system_config()
              return_dict["node"] = node
              return_dict["old_serial_number"] = serial_number
              return_dict["new_serial_number"] = new_serial_number
              template = "replace_disk_success.html"
  
          return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
          
      else:
        if "serial_number" not in request.POST:
          return_dict["error"] = "Incorrect access method. Please use the menus"
        else:
          if 'node' in request.POST:
            return_dict["node"] = request.POST["node"]
          else:
            node = si.keys()[0]
          return_dict["serial_number"] = request.POST["serial_number"]
          template = "replace_disk_conf.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
