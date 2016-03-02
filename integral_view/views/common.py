import json, time, os, shutil, tempfile, os.path, re, subprocess, sys, shutil, pwd, grp, stat,datetime

import salt.client, salt.wheel

import django.template, django
from django.conf import settings


import integralstor_common
from integralstor_common import command, db, common, audit, alerts, ntp, mail, zfs, file_processing,stats,scheduler_utils,common
from integralstor_common import cifs as cifs_common

import integralstor_unicell
from integralstor_unicell import system_info, local_users

from integral_view.utils import iv_logging

import integral_view
from integral_view.forms import common_forms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
production = common.is_production()

def dir_contents(request):
  path = request.GET.get("pool_name")
  first = request.GET.get("first")
  dirs = os.listdir(path)
  dir_dict_list = []
  if not dirs or first:
    d_dict = {'id':path, 'text':"/",'icon':'fa fa-angle-right','children':True,'data':{'dir':path},'parent':"#"}
    dir_dict_list.append(d_dict)
  if not first:
    for d in dirs:
      true = True
      if os.path.isdir(path+"/"+d):
        if first:
          parent = "#"
        else:
          parent = path
        d_dict = {'id':path+"/"+d, 'text':d,'icon':'fa fa-angle-right','children':True,'data':{'dir':path+"/"+d},'parent':parent}
      dir_dict_list.append(d_dict)
  return HttpResponse(json.dumps(dir_dict_list),mimetype='application/json')

@login_required    
def set_file_owner_and_permissions(request):
  return_dict = {}
  try:
    if 'path' not in request.REQUEST:
      raise Exception('Path not specified')
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
      return django.shortcuts.render_to_response('set_file_owner_and_permissions.html', return_dict, context_instance=django.template.context.RequestContext(request))
  
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
        return django.shortcuts.render_to_response('set_file_owner_and_permissions.html', return_dict, context_instance=django.template.context.RequestContext(request))
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

@login_required
def dashboard(request,page):
  return_dict = {}
  try:
    if request.method != 'GET':
      raise Exception('Invalid access method. Please use the menus')
    si, err = system_info.load_system_config()
    if err:
      raise Exception(err)
    if not si:
      raise Exception('Error loading system configuration')
    return_dict['system_info'] = si
    #By default show error page
    template = "logged_in_error.html"
    num_nodes_bad = 0
    total_pool = 0
    total_nodes = len(si)
    nodes = {}
    # Chart specific declarations
    today_day = (datetime.date.today()).strftime('%d') # will return 02, instead of 2.
    #today_day = datetime.datetime.today().day
    #if today_day < 10:
    #  today_day = '0%d'%today_day
    value_list = []
    time_list = []
    use_salt, err = common.use_salt()
    if err:
      raise Exception(err)
        
    ks = si.keys()
    if not ks:
      raise Exception('System configuration invalid')
    info = ks[0]
    # CPU status
    if page == "cpu":
      return_dict["page_title"] = 'CPU statistics'
      return_dict['tab'] = 'cpu_tab'
      return_dict["error"] = 'Error loading CPU statistics'
      cpu,err = stats.get_system_stats(today_day,"cpu")
      if err:
        raise Exception(err)
      value_dict = {}
      if cpu:
        for key in cpu.keys():
          value_list = []
          time_list = []
          if key == "date":
            pass
          else:
            if cpu[key]:
              for a in cpu[key]:
                time_list.append(a[0])
                value_list.append(a[1])
            value_dict[key] = value_list
      return_dict["data_dict"] = value_dict
      queue,err = stats.get_system_stats(today_day,"queue")
      if err:
        raise Exception(err)
      value_dict = {}
      if queue:
        for key in queue.keys():
          value_list = []
          time_list = []
          if key == "date":
            pass
          else:
            for a in queue[key]:
              time_list.append(a[0])
              value_list.append(a[1])
            value_dict[key] = value_list
      return_dict["data_dict_queue"] = value_dict
      return_dict['node_name'] = info
      return_dict['node'] = si[info]
      d = {}
      template = "view_cpu_status.html"
    # Hardware
    elif page == "hardware":
      return_dict["page_title"] = 'Hardware status'
      return_dict['tab'] = 'hardware_tab'
      return_dict["error"] = 'Error loading hardware status'
      d = {}
      d['ipmi_status'] = si[info]['ipmi_status']
      return_dict['hardware_status'] =  d
      return_dict['node_name'] = info
      template = "view_hardware_status.html"
    # Memory
    elif page == "memory":
      return_dict["page_title"] = 'Memory statistics'
      return_dict['tab'] = 'memory_tab'
      return_dict["error"] = 'Error loading memory statistics'
      mem,err = stats.get_system_stats(today_day,"memory")
      if err:
        raise Exception(err)
      if mem:
        for a in mem["memfree"]:
          time_list.append(a[0])
          value_list.append(a[1])
      return_dict['memory_status'] =  si[info]['memory']
      template = "view_memory_status.html"
    # Network
    elif page == "network":
      return_dict["page_title"] = 'Network statistics'
      return_dict['tab'] = 'network_tab'
      return_dict["error"] = 'Error loading Network statistics'
      network,err = stats.get_system_stats(today_day,"network")
      if err:
        raise Exception(err)
      value_dict = {}
      if network:
        for key in network.keys():
          value_list = []
          time_list = []
          if key == "date" or key == "lo":
            pass
          else:
            for a in network[key]["ifutil-percent"]:
              time_list.append(a[0])
              value_list.append(a[1])
            value_dict[key] = value_list
          
      return_dict["data_dict"] = value_dict
      print si[info]["interfaces"]
      return_dict["network_status"] = si[info]['interfaces']
      template = "view_network_status.html"
    # Services
    elif page == "services":
      return_dict["page_title"] = 'System services status'
      return_dict['tab'] = 'services_tab'
      return_dict["error"] = 'Error loading system services status'
      return_dict['services_status'] = {}
      if use_salt:
        import salt.client
        client = salt.client.LocalClient()
        winbind = client.cmd(info,'cmd.run',['service winbind status'])
        smb = client.cmd(info,'cmd.run',['service smb status'])
        nfs = client.cmd(info,'cmd.run',['service nfs status'])
        iscsi = client.cmd(info,'cmd.run',['service tgtd status'])
        ntp = client.cmd(info,'cmd.run',['service ntpd status'])
        ftp = client.cmd(info,'cmd.run',['service vsftpd status'])
        return_dict['services_status']['winbind'] = winbind[info]
        return_dict['services_status']['smb'] = smb[info]
        return_dict['services_status']['nfs'] = nfs[info]
        return_dict['services_status']['iscsi'] = iscsi[info]
        return_dict['services_status']['ntp'] = ntp[info]
        return_dict['services_status']['ftp'] = ftp[info]
      else:
        out_list, err = command.get_command_output('service winbind status', False)
        if err:
          raise Exception(err)
        if out_list:
          return_dict['services_status']['winbind'] = ' '.join(out_list)
  
        out_list, err = command.get_command_output('service smb status', False)
        if err:
          raise Exception(err)
        if out_list:
          return_dict['services_status']['smb'] = ' '.join(out_list)
  
        out_list, err = command.get_command_output('service nfs status', False)
        if err:
          raise Exception(err)
        if out_list:
          return_dict['services_status']['nfs'] = ' '.join(out_list)
  
        out_list, err = command.get_command_output('service tgtd status', False)
        if err:
          raise Exception(err)
        if out_list:
          return_dict['services_status']['iscsi'] = ' '.join(out_list)
  
        out_list, err = command.get_command_output('service ntpd status', False)
        if err:
          raise Exception(err)
        if out_list:
          return_dict['services_status']['ntp'] = ' '.join(out_list)

        out_list, err = command.get_command_output('service vsftpd status', False)
        if err:
          raise Exception(err)
        if out_list:
          return_dict['services_status']['ftp'] = ' '.join(out_list)
          
      template = "view_services_status.html"
    # Disks
    elif page == "disks":
      return_dict["page_title"] = 'Hard drives status'
      return_dict['tab'] = 'disk_tab'
      return_dict["error"] = 'Error loading hard drives status'
      sorted_disks = []
      #if 'disks' in si[info] and si[info]['disks']:
      #  for key,value in sorted(si[info]["disks"].iteritems(), key=lambda (k,v):v["position"]):
      #    sorted_disks.append(key)
      platform,err = common.get_hardware_platform()
      if not err:
        return_dict['hardware'] = platform
      return_dict['node'] = si[info]
      return_dict["disk_status"] = si[info]['disks']
      #print si[info]['disks']
      return_dict["disk_pos"] = sorted_disks
      return_dict['node_name'] = info
      template = "view_disks_status.html"
    # Pools
    elif page == "pools":
      return_dict["page_title"] = 'ZFS pools status'
      return_dict['tab'] = 'pools_tab'
      return_dict["error"] = 'Error loading ZFS pools status'
      pools, err = zfs.get_pools()
      if err:
        raise Exception(err)
      if pools:
        return_dict['pools'] = pools            
      template = "view_pools_status.html"
    return_dict["labels"] = time_list
    return_dict["data"] = value_list
    return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "dashboard_base.html"
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

  
@login_required    
def show(request, page, info = None):

  return_dict = {}
  try:

    si,err = system_info.load_system_config()
    if err:
      raise Exception(err)

    #assert False
    return_dict['system_info'] = si

    #By default show error page
    template = "logged_in_error.html"

    if page == "dir_contents":
      #CHANGE THIS TO SHOW LOCAL DIR LISTINGS!!
      return django.http.HttpResponse(dir_list,mimetype='application/json')

    elif page == "ntp_settings":

      return_dict['base_template'] = "services_base.html"
      return_dict["page_title"] = 'Network Time Protocol(NTP) settings '
      return_dict['tab'] = 'ntp_settings_tab'
      return_dict["error"] = 'Error loading Network Time Protocol(NTP) settings '
      template = "view_ntp_settings.html"
      ntp_servers, err = ntp.get_ntp_servers()
      if err:
        raise Exception(err)
      return_dict["ntp_servers"] = ntp_servers
      if "saved" in request.REQUEST:
        return_dict["saved"] = request.REQUEST["saved"]

    elif page == "integral_view_log_level":

      template = "view_integral_view_log_level.html"
      try:
        log_level = iv_logging.get_log_level_str()
      except Exception, e:
        return_dict["error"] = str(e)
      else:
        return_dict["log_level_str"] = log_level
      if "saved" in request.REQUEST:
        return_dict["saved"] = request.REQUEST["saved"]

    elif page == "email_settings":

      #print "here"
      return_dict['base_template'] = "system_base.html"
      return_dict["page_title"] = 'Email notifications settings '
      return_dict['tab'] = 'email_tab'
      return_dict["error"] = 'Error loading email notifications settings '
      d, err = mail.load_email_settings()
      if err:
        raise Exception(err)
      if not d:
        return_dict["email_not_configured"] = True
      else:
        if d["tls"]:
          d["tls"] = True
        else:
          d["tls"] = False
        if d["email_alerts"]:
          d["email_alerts"] = True
        else:
          d["email_alerts"] = False
        return_dict["email_settings"] = d
      if "saved" in request.REQUEST:
        return_dict["saved"] = request.REQUEST["saved"]
      if "not_saved" in request.REQUEST:
        return_dict["not_saved"] = request.REQUEST["not_saved"]
      if "err" in request.REQUEST:
        return_dict["err"] = request.REQUEST["err"]
      template = "view_email_settings.html"

    elif page == "audit_trail":
 
      return_dict['base_template'] = "logging_base.html"
      return_dict["page_title"] = 'System audit trail'
      return_dict['tab'] = 'view_current_audit_tab'
      return_dict["error"] = 'Error loading system audit trail'
      al = None
      template = "view_audit_trail.html"
      al, err = audit.get_lines()
      if err:
        raise Exception(err)
      return_dict["audit_list"] = al

    elif page == "node_info":
      return_dict['base_template'] = "system_base.html"
      return_dict["page_title"] = 'System configuration'
      return_dict['tab'] = 'node_info_tab'
      return_dict["error"] = 'Error loading system configuration'
      template = "view_node_info.html"
      if "from" in request.GET:
        frm = request.GET["from"]
        return_dict['frm'] = frm
      #return_dict['node'] = si[info]
      return_dict['node'] = si[si.keys()[0]]


    elif page == "alerts":

      return_dict['base_template'] = "logging_base.html"
      return_dict["page_title"] = 'System alerts'
      return_dict['tab'] = 'view_current_alerts_tab'
      return_dict["error"] = 'Error loading system alerts'
      template = "view_alerts.html"
      alerts_list, err = alerts.load_alerts()
      if err:
        raise Exception(err)
      return_dict['alerts_list'] = alerts_list


    return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

#this function takes a user argument checks if the user has administrator rights and then returns True.
#If he does not have the correct permissions, then then it returns a HTttpResponse stating No Permission to access this page.
#Takes user object as a parameter: request.user
# def is_superuser(user):
#   if user.is_superuser:
#     return True
#   else:
#     return False

def admin_login_required(view):

  def new_view(request, *args, **kwargs):
    if request.user.is_superuser:
      return view(request, *args, **kwargs)
    else:
      return django.http.HttpResponseRedirect('/login')

  return new_view

def refresh_alerts(request, random=None):
  try:
    from datetime import datetime
    cmd_list = []
    #this command will insert or update the row value if the row with the user exists.
    cmd = ["INSERT OR REPLACE INTO admin_alerts (user, last_refresh_time) values (?,?);", (request.user.username, datetime.now())]
    cmd_list.append(cmd)
    db_path, err = common.get_db_path()
    if err:
      raise Exception(err)
    test, err = db.execute_iud(db_path, cmd_list)
    if err:
      raise Exception(err)
    new_alerts_present, err = alerts.new_alerts()
    if err:
      raise Exception(err)
    if new_alerts_present:
      import json
      alerts_list, err = alerts.load_alerts(last_n = 5)
      if err:
        raise Exception(err)
      if not alerts_list:
        raise Exception('Error loading alerts')
      new_alerts = json.dumps([dict(alert=pn) for pn in alerts_list])
      return django.http.HttpResponse(new_alerts, mimetype='application/json')
    else:
      clss = "btn btn-default btn-sm"
      message = "View alerts"
      return django.http.HttpResponse("No New Alerts")
  except Exception, e:
    return django.http.HttpResponse("Error loading alerts : %s"%str(e))

@login_required
def raise_alert(request):

  return_dict = {}
  template = "logged_in_error.html"
  if "msg" not in request.REQUEST:
    return_dict["error"] = "No alert message specified."
  else:
    try:
      msg = request.REQUEST["msg"]
      ret, err = alerts.raise_alert(msg)
      if err:
        raise Exception(err)
    except Exception, e:
      return_dict["error"] = "Error logging alert : %s"%e
      iv_logging.info("Error logging alert %s"%str(e))
    else:
      return django.http.HttpResponse("Raised alert")

    return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))

    
@login_required
def configure_ntp_settings(request):

  return_dict = {}
  try:
    if request.method=="GET":
      ntp_servers, err = ntp.get_ntp_servers()
      if err:
        raise Exception(err)
      if not ntp_servers:
        form = common_forms.ConfigureNTPForm()
      else:
        form = common_forms.ConfigureNTPForm(initial={'server_list': ','.join(ntp_servers)})
      url = "edit_ntp_settings.html"
    else:
      form = common_forms.ConfigureNTPForm(request.POST)
      if form.is_valid():
        iv_logging.debug("Got valid request to change NTP settings")
        cd = form.cleaned_data
        si, err = system_info.load_system_config()
        if err:
          raise Exception(err)
        server_list = cd["server_list"]
        if ',' in server_list:
          slist = server_list.split(',')
        else:
          slist = server_list.split(' ')
        with open('/tmp/ntp.conf', 'w') as temp:
          #First create the ntp.conf file for the primary and secondary nodes
          temp.write("driftfile /var/lib/ntp/drift\n")
          temp.write("restrict default kod nomodify notrap nopeer noquery\n")
          temp.write("restrict -6 default kod nomodify notrap nopeer noquery\n")
          temp.write("logfile /var/log/ntp.log\n")
          temp.write("\n")
          for server in slist:
            temp.write("server %s iburst\n"%server)
          temp.flush()
          temp.close()
        shutil.move('/tmp/ntp.conf', '/etc/ntp.conf')
        ret, err = ntp.restart_ntp_service()
        if err:
          raise Exception(err)
        return django.http.HttpResponseRedirect("/show/ntp_settings?saved=1")
      else:
        #invalid form
        iv_logging.debug("Got invalid request to change NTP settings")
        url = "edit_ntp_settings.html"
    return_dict["form"] = form
    return django.shortcuts.render_to_response(url, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "system_base.html"
    return_dict["page_title"] = 'Modify email notifications settings'
    return_dict['tab'] = 'email_tab'
    return_dict["error"] = 'Error modifying email notifications settings'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))



@login_required 
#@django.views.decorators.csrf.csrf_exempt
def flag_node(request):

  try:
    return_dict = {}
    if "node" not in request.GET:
      raise Exception("Error flagging node. No node specified")
  
    node_name = request.GET["node"]
    blink_time = 255
    use_salt, err = common.use_salt()
    if use_salt:
      import salt.client
      client = salt.client.LocalClient()
      ret = client.cmd(node_name,'cmd.run',['ipmitool chassis identify %s' %(blink_time)])
      print ret
      if ret[node_name] == 'Chassis identify interval: %s seconds'%(blink_time):
        return django.http.HttpResponse("Success")
      else:
        raise Exception("")
    else:
      out_list, err = command.get_command_output('service winbind status')
      if err:
        raise Exception(err)
      if 'Chassis identify interval: %s seconds'%(blink_time) in out_list[0]:
        return django.http.HttpResponse("Success")
      else:
        raise Exception("")
  except Exception, e:
    return django.http.HttpResponse("Error")

    
#The below function was commented. Uncommented it. Please review it again
@admin_login_required
def reset_to_factory_defaults(request):
  return_dict = {}
  try:
    if request.method == "GET":
      #Send a confirmation screen
      return django.shortcuts.render_to_response('reset_factory_defaults_conf.html', return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      iv_logging.info("Got a request to reset to factory defaults")
      #Post request so from conf screen
  
      #Reset the ntp config file
      try :
        shutil.copyfile("%s/factory_defaults/ntp.conf"%common.get_factory_defaults_path(), '%s/ntp.conf'%fractalio.common.get_ntp_conf_path())
        pass
      except Exception, e:
        return_dict["error"] = "Error reseting NTP configuration : %s"%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
      #Remove email settings
      try:
        mail.delete_email_settings()
      except Exception, e:
        #print str(e)
        return_dict["error"] = "Error reseting mail configuration : %s."%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
      try:
        audit.rotate_audit_trail()
      except Exception, e:
        #print str(e)
        return_dict["error"] = "Error rotating the audit trail : %s."%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
      #Remove all shares 
      try:
        cifs_common.delete_all_shares()
      except Exception, e:
        #print str(e)
        return_dict["error"] = "Error deleting shares : %s."%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
      try:
        cifs_common.delete_auth_settings()
      except Exception, e:
        return_dict["error"] = "Error deleting CIFS authentication settings : %s."%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
      try:
        request.user.set_password("admin");
        request.user.save()
      except Exception, e:
        return_dict["error"] = "Error resetting admin password: %s."%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
  
      #Reset the alerts file
      try :
        shutil.copyfile("%s/factory_defaults/alerts.log"%fractalio.common.get_factory_defaults_path(), '%s/alerts.log'%fractalio.common.get_alerts_path())
      except Exception, e:
        return_dict["error"] = "Error reseting alerts : %s."%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
      #Reset all batch jobs
      try :
        l = os.listdir("%s"%fractalio.common.get_batch_files_path())
        for fname in l:
          os.remove("%s/%s"%(fractalio.common.get_batch_files_path(), fname))
      except Exception, e:
        return_dict["error"] = "Error removing scheduled batch jobs : %s."%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
      try:
        iscsi.reset_global_target_conf()
        iscsi.delete_all_targets()
        iscsi.delete_all_initiators()
        iscsi.delete_all_auth_access_groups()
        iscsi.delete_all_auth_access_users()
      except Exception, e:
        return_dict["error"] = "Error resetting ISCSI configuration : %s."%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
      try:
        # Create commands to stop and delete volumes. Remove peers from cluster.
        vil = volume_info.get_volume_info_all()
        scl = system_info.load_system_config()
        d = gluster_commands.create_factory_defaults_reset_file(scl, vil)
        if not "error" in d:
          audit.audit("factory_defaults_reset_start", "Scheduled reset of the system to factory defaults.",  request.META["REMOTE_ADDR"])
          return django.http.HttpResponseRedirect('/show/batch_start_conf/%s'%d["file_name"])
        else:
          return_dict["error"] = "Error initiating a reset to system factory defaults : %s"%d["error"]
          return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
      except Exception, e:
        return_dict["error"] = "Error creating factory defaults reset batch file : %s."%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

@login_required
def internal_audit(request):

  response = django.http.HttpResponse()
  if request.method == "GET":
    response.write("Error!")
  else:
    if not "who" in request.POST or request.POST["who"] != "batch":
      response.write("Unknown requester")
      return response
    if (not "audit_action" in request.POST) or (not "audit_str" in request.POST):
      response.write("Insufficient information!")
    else:
      audit.audit(request.POST["audit_action"], request.POST["audit_str"], "0.0.0.0")
    response.write("Success")
  return response

def reload_manifest(request):
  return_dict = {}
  try:
    if request.method == "GET":
      from integralstor_common import manifest_status as iu
      mi, err = iu.generate_manifest_info()
      #print mi, err
      if err:
        raise Exception(err)
      if not mi:
        raise Exception('Could not load new configuration')
      return_dict["mi"] = mi[mi.keys()[0]] # Need the hostname here. 
      return django.shortcuts.render_to_response("reload_manifest.html", return_dict, context_instance=django.template.context.RequestContext(request))
    elif request.method == "POST":
      common_python_scripts_path, err = common.get_common_python_scripts_path()
      if err:
        raise Exception(err)
      ss_path, err = common.get_system_status_path()
      if err:
        raise Exception(err)
      #(ret,rc), err = command.execute_with_rc("python %s/generate_manifest.py %s"%(common_python_scripts_path, ss_path))
      ret, err = command.get_command_output("python %s/generate_manifest.py %s"%(common_python_scripts_path, ss_path))
      #print 'mani', ret, err
      if err:
        raise Exception(err)
      #(ret,rc), err = command.execute_with_rc("python %s/generate_status.py %s"%(common.get_python_scripts_path(), common.get_system_status_path()))
      ret, err = command.get_command_output("python %s/generate_status.py %s"%(common_python_scripts_path, ss_path))
      #print 'stat', ret, err
      if err:
        raise Exception(err)
      return django.http.HttpResponseRedirect("/show/node_info/")
  except Exception, e:
    return_dict['base_template'] = "system_base.html"
    return_dict["page_title"] = 'Reload system configuration'
    return_dict['tab'] = 'node_info_tab'
    return_dict["error"] = 'Error reloading system configuration'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def list_cron_jobs(request):
  return_dict = {}
  try:
    cron_jobs,err = scheduler_utils.list_all_cron()
    if err:
      raise Exception(err)
    return_dict["cron_list"] = cron_jobs
    return django.shortcuts.render_to_response("view_cron_jobs.html", return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "scheduler_base.html"
    return_dict["page_title"] = 'Scheduled jobs'
    return_dict['tab'] = 'view_cron_jobs_tab'
    return_dict["error"] = 'Error loading scheduled jobs information'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def download_cron_log(request):
  response = django.http.HttpResponse()
  cron_name = request.POST.get('cron_name')
  try:
    response['Content-disposition'] = 'attachment; filename='+cron_name.replace(" ","_")+'.log'
    response['Content-type'] = 'application/x-compressed'
    with open(common.get_log_folder_path()+"/"+cron_name.replace(" ","_")+".log", 'rb') as f:
      byte = f.read(1)
      while byte:
        response.write(byte)
        byte = f.read(1)
        response.flush()
  except Exception as e:
    return django.http.HttpResponse(e)
  return response

def remove_cron_job(request):
  try:
    cron_name = request.POST.get('cron_name')
    delete,err = scheduler_utils.delete_cron_with_comment(cron_name)
    if err:
      raise Exception(err)
    if delete:
      return django.http.HttpResponseRedirect("/list_cron_jobs")
    else:
      raise Exception('Error deleting a scheduled job')
  except Exception, e:
    return_dict['base_template'] = "scheduler_base.html"
    return_dict["page_title"] = 'Scheduled jobs'
    return_dict['tab'] = 'view_cron_jobs_tab'
    return_dict["error"] = 'Error removing scheduled jobs information'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_background_tasks(request):
  return_dict = {}
  db_path = settings.DATABASES["default"]["NAME"]
  try:
    return_dict["back_jobs"] = scheduler_utils.get_background_jobs(db_path)[0]
    return django.shortcuts.render_to_response("view_background_tasks.html", return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "scheduler_base.html"
    return_dict["page_title"] = 'Background jobs'
    return_dict['tab'] = 'view_background_tasks_tab'
    return_dict["error"] = 'Error retriving background tasks'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_task_details(request,task_id):
  return_dict = {}
  db_path = settings.DATABASES["default"]["NAME"]
  try:
    task_name,err = scheduler_utils.get_background_job(db_path,int(task_id))
    details,err = scheduler_utils.get_task_details(db_path,int(task_id))
    if details[0]['retries'] == -2:
      status = ""
      # This code always updates the 0th element of the command list. This is assuming that we will only have one long running command.
      if os.path.isfile("/tmp/%d.log"%int(task_id)):
        with open('/tmp/%d.log'%int(task_id)) as output:
          status = status + ''.join(output.readlines())
      details[0]['output'] = status
    return_dict["task_name"] = task_name[0]["task_name"]
    return_dict["tasks"] = details
    return django.shortcuts.render_to_response("view_task_details.html", return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "scheduler_base.html"
    return_dict["page_title"] = 'Background jobs'
    return_dict['tab'] = 'view_background_tasks_tab'
    return_dict["error"] = 'Error retriving background task details'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
