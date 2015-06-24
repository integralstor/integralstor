import django, django.template

import integralstor_common
import integralstor_unicell
from integralstor_common import networking, audit

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
