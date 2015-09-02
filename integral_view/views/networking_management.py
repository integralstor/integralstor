import django, django.template

import integralstor_common
import integralstor_unicell
from integralstor_common import networking, audit, command, common
from django.contrib.auth.decorators import login_required

import socket

import integral_view
from integral_view.forms import networking_forms
  
def view_interfaces(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'
    nics, err = networking.get_interfaces()
    if not nics and err:
      return_dict["error"] = "Error loading network interface information : %s"%err
    bonds, err = networking.get_bonding_info_all()
    if not bonds and err:
      return_dict["error"] = "Error loading network bonding information : %s"%err
  
    if not "error" in return_dict:
      if "action" in request.GET:
        if request.GET["action"] == "saved":
          conf = "Network interface information successfully updated"
        if request.GET["action"] == "removed_bond":
          conf = "Network bond successfully removed"
        if request.GET["action"] == "state_down":
          conf = "Network interface successfully disabled. The state change may take a couple of seconds to reflect on this page so please refresh it to check the updated status."
        if request.GET["action"] == "state_up":
          conf = "Network interface successfully enabled. The state change may take a couple of seconds to reflect on this page so please refresh it to check the updated status."
        if request.GET["action"] == "created_bond":
          conf = "Network bond successfully created. Please edit the address information for the bond in order to use it."
        return_dict["conf"] = conf
      return_dict["nics"] = nics
      return_dict["bonds"] = bonds
      template = "view_interfaces.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_nic(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'
    if 'name' not in request.REQUEST:
      return_dict["error"] = "Error loading network interface information : No interface name specified."
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
    
    name = request.REQUEST['name']
    interfaces, err = networking.get_interfaces()

    if not interfaces and err:
      return_dict["error"] = "Error loading network interface information : %s"%err
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
    elif name not in interfaces:
      return_dict["error"] = "Error loading network interface information : Specified interface not found"
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))

    return_dict['nic'] = interfaces[name]
    return_dict['name'] = name
      
    template = "view_nic.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def set_interface_state(request):

  return_dict = {}
  try:
    if 'name' not in request.REQUEST:
      return_dict["error"] = "Error setting interface state - No interface name specified. Please use the menus"%str(e)
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
    if 'state' not in request.REQUEST:
      return_dict["error"] = "Error setting interface state - No state specified. Please use the menus"%str(e)
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

    name = request.REQUEST["name"]
    return_dict["name"] = name
    state = request.REQUEST["state"]
    return_dict["state"] = state

    if request.method == "GET" and state == 'down':
      #Return the conf page
      return django.shortcuts.render_to_response("set_interface_state_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      result, err = networking.set_interface_state(name, state)
      if not result:
        if not err:
          return_dict["error"] = "Error setting interface state"
        else:
          return_dict["error"] = "Error setting interface state - %s"%err
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
 
      audit_str = "Set the state of network interface %s to %s"%(name, state)
      audit.audit("set_interface_state", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_interfaces?action=state_%s'%state)
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_bond(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'
    if 'name' not in request.REQUEST:
      return_dict["error"] = "Error loading network bond information : No bond name specified."
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
    
    name = request.REQUEST['name']

    interfaces, err = networking.get_interfaces()
    if not interfaces and err:
      return_dict["error"] = "Error loading network interface information : %s"%err
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
    elif name not in interfaces:
      return_dict["error"] = "Error loading network interface information : Specified interface not found"
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))

    bond, err = networking.get_bonding_info(name)
    if not bond and err:
      return_dict["error"] = "Error loading network bond information : %s"%err
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
    elif not bond:
      return_dict["error"] = "Error loading network bond information : Specified bond not found"
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))

    return_dict['nic'] = interfaces[name]
    return_dict['bond'] = bond
    return_dict['name'] = name
      
    template = "view_bond.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def edit_interface_address(request):
  return_dict = {}
  try:
    if 'name' not in request.REQUEST:
      raise Exception("Interface name not specified. Please use the menus.")

    name = request.REQUEST["name"]
    interfaces, err = networking.get_interfaces()

    if not interfaces and err:
      return_dict["error"] = "Error loading network interface information : %s"%err
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
    elif name not in interfaces:
      return_dict["error"] = "Error loading network interface information : Specified interface not found"
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
    return_dict['nic'] = interfaces[name]

    if request.method == "GET":

      initial = {}
      initial['name'] = name
      if 'bootproto' in interfaces[name] and interfaces[name]['bootproto'] == 'dhcp':
        initial['addr_type'] = 'dhcp'
      else:
        initial['addr_type'] = 'static'
        if 'addresses' in interfaces[name] and 'AF_INET' in interfaces[name]['addresses'] and interfaces[name]['addresses']['AF_INET']:
          initial['ip'] = interfaces[name]['addresses']['AF_INET'][0]['addr']
          initial['netmask'] = interfaces[name]['addresses']['AF_INET'][0]['netmask']
      print interfaces[name]
      if 'gateways' in interfaces[name] and interfaces[name]['gateways']:
        if interfaces[name]['gateways'][0][2]:
          initial['default_gateway'] = interfaces[name]['gateways'][0][0]
      print initial

      form = networking_forms.NICForm(initial=initial)
      return_dict['form'] = form
      return django.shortcuts.render_to_response("edit_interface_address.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = networking_forms.NICForm(request.POST)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("edit_interface_address.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      result_str = ""
      audit_str = "Changed the following dataset properties for dataset %s : "%name
      success = False
      try :
        result, err = networking.set_interface_ip_info(cd['name'], cd)
        if not result:
          if err:
            raise Exception(err)
          else:
            raise Exception('Error setting interface IP address ')
        result, err = networking.restart_networking()
        if not result:
          if err:
            raise Exception(err)
          else:
            raise Exception('Error setting interface IP address. Could not restart networking services.')
        audit_str = 'Changed the address of %s. New values are IP : %s, netmask: %s'%(cd['name'], cd['ip'], cd['netmask']) 
        if 'default_gateway' in cd:
          audit_str += ', default gateway : %s'%cd['default_gateway']
        audit.audit("edit_interface_address", audit_str, request.META["REMOTE_ADDR"])
                
      except Exception, e:
        return_dict["error"] = "Error saving interface address information - %s"%str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
 
      return django.http.HttpResponseRedirect('/view_nic?name=%s&result=addr_changed'%(name))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_bond(request):
  return_dict = {}
  try:

    interfaces, err = networking.get_interfaces()
    if not interfaces:
      return_dict["error"] = "Error loading network interface information : No interfaces found"
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
    if err:
      return_dict["error"] = "Error loading network interface information : %s"%err
      return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))

    bonds, err = networking.get_bonding_info_all()
    if not bonds and err:
      return_dict["error"] = "Error loading network bonding information : %s"%err

    return_dict['interfaces'] = interfaces
    if_list = []
    existing_bonds = []
    for if_name, iface in interfaces.items():
      if 'bonding_master' in iface and iface['bonding_master']:
        existing_bonds.append(if_name)
        continue
      if 'slave_to' in iface and iface['slave_to']:
        continue
      if 'eth' not in if_name:
        continue
      if_list.append(if_name)
    if request.method == "GET":
      form = networking_forms.CreateBondForm(interfaces = if_list, existing_bonds = existing_bonds)
      return_dict['form'] = form
      return django.shortcuts.render_to_response("create_bond.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = networking_forms.CreateBondForm(request.POST, interfaces = if_list, existing_bonds = existing_bonds)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("create_bond.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      try :
        result, err = networking.create_bond(cd['name'], cd['slaves'], int(cd['mode']))
        if not result:
          if not err:
            raise Exception('Unknown error!')
          else:
            raise Exception(err)
      except Exception, e:
        return_dict["error"] = "Error creating network bond- %s"%str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
 
      audit_str = "Created a network bond named %s with slaves"%(cd['name'], ','.join(cd['slaves']))
      audit.audit("create_bond", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_interfaces?action=created_bond')
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def remove_bond(request):

  return_dict = {}
  try:
    if 'name' not in request.REQUEST:
      return_dict["error"] = "Error removing bond - No bond name specified. Please use the menus"%str(e)
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))

    name = request.REQUEST["name"]
    return_dict["name"] = name

    if request.method == "GET" :
      #Return the conf page
      return django.shortcuts.render_to_response("remove_bond_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      result, err = networking.remove_bond(name)
      if not result:
        if not err:
          return_dict["error"] = "Error removing bond"
        else:
          return_dict["error"] = "Error removing bond - %s"%err
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
 
      audit_str = "Removed network bond %s"%(name)
      audit.audit("remove_bond", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_interfaces?action=removed_bond')
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_hostname(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'
    hostname = socket.gethostname()
    domain_name,err = networking.get_domain_name()
    if err:
      print err
      return_dict["error"] = "Error getting domain name : %s"%err
  
    if not "error" in return_dict:
      if "action" in request.GET:
        if request.GET["action"] == "saved":
          conf = "Hostname information successfully updated"
        return_dict["conf"] = conf
      return_dict['domain_name'] = domain_name
      return_dict['hostname'] = hostname
      template = "view_hostname.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def edit_hostname(request):
  return_dict = {}
  try:

    hostname = socket.gethostname()
    if request.method == "GET":
      hostname = socket.gethostname()
      domain_name,err = networking.get_domain_name()
      if err:
        print err
        raise Exception(err)

      initial = {}
      initial['hostname'] = hostname
      initial['domain_name'] = domain_name
      print initial

      form = networking_forms.EditHostnameForm(initial=initial)
      return_dict['form'] = form
      return django.shortcuts.render_to_response("edit_hostname.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = networking_forms.EditHostnameForm(request.POST)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("edit_hostname.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      result_str = ""
      try :
        domain_name = None
        if 'domain_name' in cd:
          domain_name = cd['domain_name']
        result, err = networking.set_hostname(cd['hostname'], domain_name)
        if not result:
          if err:
            raise Exception('Error setting hostname : %s'%err)
          else:
            raise Exception('Error setting hostname')
        result, err = networking.set_domain_name(domain_name)
        if not result:
          if err:
            raise Exception('Error setting domain name : %s'%err)
          else:
            raise Exception('Error setting domain name')
        python_scripts_path, err = common.get_python_scripts_path()
        if err:
          raise Exception(err)
        ss_path, err = common.get_system_status_path()
        if err:
          raise Exception(err)

        (ret,rc), err = command.execute_with_rc("python %s/generate_manifest.py %s"%(python_scripts_path, ss_path))
        if err:
          raise Exception(err)
        if rc != 0:
          err = ''
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
        (ret,rc), err = command.execute_with_rc("python %s/generate_status.py %s"%(python_scripts_path, ss_path))
        if rc != 0:      
        if err:
          raise Exception(err)
          err = ''
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
  
        audit_str = "Hostname set to %s."%cd['hostname']
        if 'domain_name' in cd:
          audit_str += 'Domain name set to %s'%cd['domain_name']
        ret, err = audit.audit("edit_hostname", audit_str, request.META["REMOTE_ADDR"])
        if err:
          raise Exception(err)
                
      except Exception, e:
        return_dict["error"] = "Error setting hostname information - %s"%str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
 
      return django.http.HttpResponseRedirect('/view_hostname?result=saved')
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_dns_nameservers(request):
  return_dict = {}
  try:
    ns_list, err = networking.get_name_servers()
    if err:
      print err
      return_dict["error"] = "Error getting DNS name servers : %s"%err
  
    if not "error" in return_dict:
      if "action" in request.GET:
        if request.GET["action"] == "saved":
          conf = "Name servers successfully updated"
        return_dict["conf"] = conf
      return_dict['name_servers'] = ns_list
      template = "view_dns_nameservers.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


@login_required
def edit_dns_nameservers(request):

  return_dict = {}
  try:
    ns_list, err = networking.get_name_servers()
    if request.method=="GET":
      if not ns_list:
        form = networking_forms.DNSNameServersForm()
      else:
        form = networking_forms.DNSNameServersForm(initial={'nameservers': ','.join(ns_list)})
      url = "edit_dns_nameservers.html"
    else:
      form = networking_forms.DNSNameServersForm(request.POST)
      if form.is_valid():
        cd = form.cleaned_data
        nameservers = cd["nameservers"]
        if ',' in nameservers:
          slist = nameservers.split(',')
        else:
          slist = nameservers.split(' ')
        res, err = networking.set_name_servers(slist)
        if not res:
          if err:
            raise Exception(err)
          else:
            raise Exception('Error updating nameservers')
        audit_str = "Updated the DNS nameserver list to %s"%nameservers
        audit.audit("set_dns_nameservers", audit_str, request.META["REMOTE_ADDR"])
        return django.http.HttpResponseRedirect('/view_dns_nameservers?action=saved')
      else:
        #invalid form
        url = "edit_dns_nameservers.html"
    return_dict["form"] = form
    return django.shortcuts.render_to_response(url, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    s = str(e)
    return_dict["error"] = "An error occurred when processing your request : %s"%s
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
