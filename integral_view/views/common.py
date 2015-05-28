import json, time, os, shutil, tempfile, os.path, re, subprocess, sys, shutil

import salt.client, salt.wheel

import django.template, django
from django.conf import settings


import integralstor_common
from integralstor_common import command, db, common, audit, alerts, ntp, mail, zfs

import integralstor_unicell
from integralstor_unicell import system_info

from integral_view.utils import iv_logging

import integral_view
from integral_view.forms import common_forms
from integral_view.samba import samba_settings
from django.contrib.auth.decorators import login_required

production = common.is_production()

@login_required    
def show(request, page, info = None):

  return_dict = {}
  try:

    assert request.method == 'GET'

    si = system_info.load_system_config()

    #assert False
    return_dict['system_info'] = si

    #By default show error page
    template = "logged_in_error.html"

    if page == "dir_contents":
      #CHANGE THIS TO SHOW LOCAL DIR LISTINGS!!
      return django.http.HttpResponse(dir_list,mimetype='application/json')

    elif page == "ntp_settings":

      template = "view_ntp_settings.html"
      try:
        ntp_servers = ntp.get_ntp_servers()
      except Exception, e:
        return_dict["error"] = str(e)
      else:
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
      try:
        d = mail.load_email_settings()
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
      except Exception, e:
        iv_logging.debug("error loading email settings %s"%e)
        return_dict["error"] = str(e)

    elif page == "audit_trail":

      al = None
      try:
        al = audit.get_lines()
      except Exception, e:
        return_dict["error"] = str(e)
      else:
        template = "view_audit_trail.html"
        return_dict["audit_list"] = al

    elif page == "node_status":
      
      template = "view_node_status.html"
      if "from" in request.GET:
        frm = request.GET["from"]
        return_dict['frm'] = frm
      sorted_disks = []
      for key,value in sorted(si[info]["disks"].iteritems(), key=lambda (k,v):v["position"]):
        sorted_disks.append(key)
      si[info]["disk_pos"] = sorted_disks
      return_dict['node'] = si[info]
      import salt.client
      client = salt.client.LocalClient()
      winbind = client.cmd(info,'cmd.run',['service winbind status'])
      smb = client.cmd(info,'cmd.run',['service smb status'])
      return_dict['winbind'] = winbind[info]
      return_dict['smb'] = smb[info]
      return_dict['node_name'] = info


    elif page == "node_info":

      template = "view_node_info.html"
      if "from" in request.GET:
        frm = request.GET["from"]
        return_dict['frm'] = frm
      return_dict['node'] = si[info]


    elif page == "system_config":

      template = "view_system_config.html"

    elif page == "system_status":
     #Disk Status page and system status page has been integrated.
     #assert False

      #Get the disk status
      disk_status = {}
      disk_new = {}

      if request.GET.get("node_id") is not None:
        disk_status = si[request.GET.get("node_id")]
        return_dict["disk_status"] = {}
        return_dict["disk_status"][request.GET.get("node_id")] = disk_status
        template = "view_disk_status_details.html"

      else:
        """
          Iterate the system information, and get the following data :
            1. The status of every disk
            2. The status of the pool
            3. The name of the pool
            4. Calcualte the background_color
            Format : {'node_id':{'name':'pool_name','background_color':'background_color','disks':{disks_pool}}}

        """
        for key, value in si.iteritems():
          #count the failures in case of Offline or degraded
          disk_failures = 0
          #Default background color
          background_color = "bg-green" 
          disk_new[key] = {}
          disk_new[key]["disks"] = {}
          for disk_key, disk_value in si[key]["disks"].iteritems():
            #print disk_key, disk_value
            if disk_value["rotational"]:
              disk_new[key]["disks"][disk_key] = disk_value["status"]
            #print disk_value["status"]
            if disk_value["status"] != "PASSED":
              disk_failures += 1
            if disk_failures >= 1:
              background_color = "bg-yellow"
            if disk_failures >= 4:
              background_color == "bg-red"
          
          if si[key]['node_status_str'] == "Degraded":
            background_color = "bg-yellow"
          #print type(si[key]["pools"][0]["state"])
          if si[key]["pools"][0]["state"] == unicode("ONLINE"):
            background_color == "bg-red"
          disk_new[key]["background_color"] = background_color
          disk_new[key]["name"] = si[key]["pools"][0]["name"]
          sorted_disks = []
          for key1,value1 in sorted(si[key]["disks"].iteritems(), key=lambda (k,v):v["position"]):
            sorted_disks.append(key1)
          disk_new[key]["disk_pos"] = sorted_disks
          #print disk_new
          #disk_new[key]["info"] = pool_status
          '''
          else:             
            disk_status[key] = {}
            if si[key]["node_status"] != -1:
              disk_status[key]["disks"] = {}
              for disk_key, disk_value in si[key]["disks"].iteritems():
                #print disk_key, disk_value
                if disk_value["rotational"]:
                  disk_status[key]["disks"][disk_key] = disk_value["status"]
                #print disk_value["status"]
                if disk_value["status"] != "PASSED":
                  disk_failures += 1
                if disk_failures >= 1:
                  background_color = "bg-yellow"
                if disk_failures >= 4:
                  background_color == "bg-red"

              if si[key]['node_status_str'] == "Degraded":
                background_color = "bg-yellow"
              #print type(si[key]["pools"][0]["state"])
              if si[key]["pools"][0]["state"] == unicode("ONLINE"):
                background_color == "bg-red"
              disk_status[key]["background_color"] = background_color
              disk_status[key]["name"] = si[key]["pools"][0]["name"]
              sorted_disks = []
              for key1,value1 in sorted(si[key]["disks"].iteritems(), key=lambda (k,v):v["position"]):
                sorted_disks.append(key1)
              disk_status[key]["disk_pos"] = sorted_disks
              #print disk_status
              #disk_status[key]["info"] = pool_status
            else:
              disk_status[key] = {}
              disk_status[key]["background_color"] = "bg-red"
              disk_status[key]["disk_pos"] = {}
              disk_status[key]["name"] = "Unknown"
        '''
        
        template = "view_disk_status.html"
        return_dict["disk_status"] = disk_status
        return_dict["disk_new"] = disk_new



    elif page == "dashboard":
      num_nodes_bad = 0
      total_pool = 0
      total_nodes = len(si)
      nodes = {}

      for k, v in si.items():
        nodes[k] = v["node_status"]
        if v["node_status"] != 0:
          num_nodes_bad += 1
          
      pools, err = zfs.get_pools()
      if pools:
        return_dict["pools"] = pools            
      return_dict["num_nodes_bad"] = num_nodes_bad            
      return_dict["total_nodes"] = total_nodes            
      return_dict["nodes"] = nodes            
      template = "view_dashboard.html"

    elif page == "alerts":

      template = "view_alerts.html"
      alerts_list = alerts.load_alerts()
      return_dict['alerts_list'] = alerts_list


    return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    if "Another transaction is in progress".lower() in s.lower():
      return_dict["error"] = "An underlying storage operation has locked a volume so we are unable to process this request. Please try after a couple of seconds"
    else:
      return_dict["error"] = "An error occurred when processing your request : %s"%s
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
    from datetime import datetime
    cmd_list = []
    #this command will insert or update the row value if the row with the user exists.
    cmd = ["INSERT OR REPLACE INTO admin_alerts (user, last_refresh_time) values (?,?);", (request.user.username, datetime.now())]
    cmd_list.append(cmd)
    test = db.execute_iud("%s/integral_view_config.db"%common.get_db_path(), cmd_list)
    if alerts.new_alerts():
      import json
      new_alerts = json.dumps([dict(alert=pn) for pn in alerts.load_alerts()])
      return django.http.HttpResponse(new_alerts, mimetype='application/json')
    else:
      clss = "btn btn-default btn-sm"
      message = "View alerts"
      return django.http.HttpResponse("No New Alerts")

@login_required
def raise_alert(request):

  return_dict = {}
  template = "logged_in_error.html"
  if "msg" not in request.REQUEST:
    return_dict["error"] = "No alert message specified."
  else:
    try:
      msg = request.REQUEST["msg"]
      alerts.raise_alert(msg)
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
      ntp_servers = ntp.get_ntp_servers()
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
        si = system_info.load_system_config()
        server_list = cd["server_list"]
        if ',' in server_list:
          slist = server_list.split(',')
        else:
          slist = server_list.split(' ')
        try:
          primary_server = "primary.fractalio.lan"
          secondary_server = "secondary.fractalio.lan"
          #First create the ntp.conf file for the primary and secondary nodes
          temp = tempfile.NamedTemporaryFile(mode="w")
          temp.write("driftfile /var/lib/ntp/drift\n")
          temp.write("restrict default kod nomodify notrap nopeer noquery\n")
          temp.write("restrict -6 default kod nomodify notrap nopeer noquery\n")
          temp.write("includefile /etc/ntp/crypto/pw\n")
          temp.write("keys /etc/ntp/keys\n")
          temp.write("\n")
          for server in slist:
            temp.write("server %s iburst\n"%server)
          temp.flush()
          shutil.move(temp.name, "%s/ntp/primary_ntp.conf"%fractalio.common.get_admin_vol_mountpoint())
          #client = salt.client.LocalClient()
          #client.cmd('roles:master', 'cp.get_file', ["salt://tmp/%s"%os.path.basename(temp.name), '%s/ntp.conf'%fractalio.common.get_ntp_conf_path()], expr_form='grain')
          #client.cmd('roles:master', 'cmd.run_all', ["service ntpd restart"], expr_form='grain')
          #shutil.copyfile(temp.name, '%s/ntp.conf'%settings.NTP_CONF_PATH)
          temp1 = tempfile.NamedTemporaryFile(mode="w")
          temp1.write("server %s iburst\n"%primary_server)
          temp1.write("server %s iburst\n"%secondary_server)
          for s in si.keys():
            temp1.write("peer %s iburst\n"%s)
          temp1.write("server 127.127.1.0\n")
          temp1.write("fudge 127.127.1.0 stratum 10\n")
          temp1.flush()
          shutil.move(temp1.name, "%s/ntp/secondary_ntp.conf"%fractalio.common.get_admin_vol_mountpoint())
          #client.cmd('role:secondary', 'cp.get_file', ["salt://tmp/%s"%os.path.basename(temp1.name), '%s/ntp.conf'%fractalio.common.get_ntp_conf_path()], expr_form='grain')
          #client.cmd('role:secondary', 'cmd.run_all', ["service ntpd restart"], expr_form='grain')
          #shutil.copyfile(temp.name, '/tmp/ntp.conf')
  
          '''
          lines = ntp.get_non_server_lines()
          if lines:
            for line in lines:
              temp.write("%s\n"%line)
          '''
          #ntp.restart_ntp_service()
        except Exception, e:
          return_dict["error"] = "Error updating NTP information : %s"%e
          return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance = django.template.context.RequestContext(request))
        else:
          return django.http.HttpResponseRedirect("/show/ntp_settings?saved=1")
      else:
        #invalid form
        iv_logging.debug("Got invalid request to change NTP settings")
        url = "edit_ntp_settings.html"
    return_dict["form"] = form
    return django.shortcuts.render_to_response(url, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    if "Another transaction is in progress".lower() in s.lower():
      return_dict["error"] = "An underlying storage operation has locked a volume so we are unable to process this request. Please try after a couple of seconds"
    else:
      return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))



@login_required 
#@django.views.decorators.csrf.csrf_exempt
def flag_node(request):

  return_dict = {}
  if "node" not in request.GET:
    return_dict["error"] = "Error flagging node. No node specified"
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance = django.template.context.RequestContext(request))

  node_name = request.GET["node"]
  import os
  import salt.client

  client = salt.client.LocalClient()
  if production:
    blink_time = 255
  else:
    blink_time = 20 #default = 255
  ret = client.cmd(node_name,'cmd.run',['ipmitool chassis identify %s' %(blink_time)])
  print ret
  if ret[node_name] == 'Chassis identify interval: %s seconds'%(blink_time):
    return django.shortcuts.render_to_response("node_flagged.html", return_dict, context_instance = django.template.context.RequestContext(request))
  else:
    return_dict["error"] = "err"
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance = django.template.context.RequestContext(request))
  # str = "/opt/fractal/bin/client %s ipmitool chassis identify 255"%node_name
  # iv_logging.debug("Flagging node %s using %s"%(node_name,str))
  # r, rc = command.execute_with_rc("/opt/fractal/bin/client %s ipmitool chassis identify 255"%node_name)
  # err = ""
  # if rc == 0:
  #   l = command.get_output_list(r)
  #   if l:
  #     for ln in l:
  #       if ln.find("Success"):
  #         return django.shortcuts.render_to_response("node_flagged.html", return_dict, context_instance = django.template.context.RequestContext(request))
  #       err += ln
  #       err += "."
  # else:
  #   err = "Error contacting node. Node down?"

    
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
        shutil.copyfile("%s/factory_defaults/ntp.conf"%fractalio.common.get_factory_defaults_path(), '%s/ntp.conf'%fractalio.common.get_ntp_conf_path())
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
        samba_settings.delete_all_shares()
      except Exception, e:
        #print str(e)
        return_dict["error"] = "Error deleting shares : %s."%e
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
  
      try:
        samba_settings.delete_auth_settings()
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
    if "Another transaction is in progress".lower() in s.lower():
      return_dict["error"] = "An underlying storage operation has locked a volume so we are unable to process this request. Please try after a couple of seconds"
    else:
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






###  THE CODES BELOW ARE MAINTAINED FOR EITER HISTORICAL PURPOSES OR AS A PART OF BACKUP PROCESS.
###  PLEASE DO CONFIRM BELOW DELETING OR DELETE WHEN PUSHING THE DEVELOP TO MASTER AS A PROCESS OF CODE CLEANUP.

'''
def accept_manifest(request):
  if request.method == "GET":
    return_dict["error"] = "Invalid access. Please use the GUI."
    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
  return_dict = {}
  try:
    dir = settings.BATCH_COMMANDS_DIR
  except:
    dir = "."
  manifest = request.POST["manifest"]
  if not os.path.isfile("%s/manifest/%s"%(settings.BASE_FILE_PATH, manifest)):
    return_dict["error"] = "Specified configuration does not exist. Please use the GUI."
    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
  try :
    shutil.move("%s/manifest/%s"%(settings.BASE_FILE_PATH, manifest), "%s/master.manifest"%settings.SYSTEM_INFO_DIR)
  except Exception, e:
    return_dict['error'] = 'Error updating to the new configuratio : %s'%e
    return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

  return django.shortcuts.render_to_response('accept_manifest_conf.html', return_dict, context_instance=django.template.context.RequestContext(request))



def del_email_settings(request):

  try:
    mail.delete_email_settings()
    return django.http.HttpResponse("Successfully cleared email settings.")
  except Exception, e:
    iv_logging.debug("Error clearing email settings %s"%e)
    return django.http.HttpResponse("Problem clearing email settings %s"%str(e))

def require_login(view):

  def new_view(request, *args, **kwargs):
    if request.user.is_authenticated():
      return view(request, *args, **kwargs)
    else:
      return django.http.HttpResponseRedirect('/login')

  return new_view

def require_admin_login(view):

  def new_view(request, *args, **kwargs):
    if request.user.is_authenticated() and request.user.username == 'dlcadmin':
      return view(request, *args, **kwargs)
    else:
      return django.http.HttpResponseRedirect('/login')

  return new_view
    elif page=="refresh_status":
      if "file_name" not in request.REQUEST:
        return_dict['error'] = 'Invalid request. No status file specified'
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
      file_name = request.REQUEST["file_name"]
      if not os.path.isfile("%s/status/%s"%(settings.BASE_FILE_PATH, file_name)):
        return_dict['error'] = 'The requested status file does not exist'
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
      o = ""
      with open("%s/status/%s"%(settings.BASE_FILE_PATH, file_name), "r") as f:
        l = f.readline()
        #print l
        while l:
          tl = l.rstrip()
          if tl == "==done==":
            #print "done"
            o += '<script type="text/javascript">'
            o += 'window.done = 1;'
            o+= '</script>'
            break
          else:
            #print l
            o += l
            o += "<br>"
          l = f.readline()
      return django.http.HttpResponse(o)
'''
