import os, socket, re, sys
from integralstor_common import networking, command

def configure_interface():

  try :
    os.system('clear')
    interfaces, err = networking.get_interfaces()
    if err:
      raise Exception('Error retrieving interface information : %s'%err)
    if not interfaces:
      raise Exception('No interfaces detected')
    print
    print
    print 'Integralstor Unicell interface configuration'
    print '--------------------------------------------'
    print
    print
    print 'Current network interfaces : '
    print
    for if_name, iface in interfaces.items():
      if if_name.startswith('lo'):
        continue
      print '- %s'%if_name
    print
    
    valid_input = False
    while not valid_input:
      ifname = raw_input('Enter the name of the interface that you wish to configure : ')
      if ifname not in interfaces or ifname.startswith('lo'):
        print 'Invalid interface name'
      else:
        valid_input = True
    print
    ip_info, err = networking.get_ip_info(ifname)
    '''
    if err:
      raise Exception('Error retrieving interface information : %s'%err)
    '''
    if ip_info:
      ip = ip_info["ipaddr"]
      netmask = ip_info["netmask"]
    else:
      ip = None
      netmask = None
    #print ip_info
    old_boot_proto, err = networking.get_interface_bootproto(ifname)
    if err:
      raise Exception('Error retrieving interface information : %s'%err)
    



    config_changed = False

    str_to_print = "Configure for DHCP or static addressing (dhcp/static)? : "
    valid_input = False
    while not valid_input :
      input = raw_input(str_to_print)
      if input:
        if input.lower() in ['static', 'dhcp']:
          valid_input = True
          boot_proto = input.lower()
          if boot_proto != old_boot_proto:
            config_changed = True
      if not valid_input:
        print "Invalid value. Please try again."
    print


    if boot_proto == 'static':
      if ip:
        str_to_print = "Enter IP address (currently %s, press enter to retain current value) : "%ip
      else:
        str_to_print = "Enter IP address (currently not set) : "
      valid_input = False
      while not valid_input :
        input = raw_input(str_to_print)
        if input:
          ok, err = networking.validate_ip(input)
          if err:
            raise Exception('Error validating IP : %s'%err)
          if ok:
            valid_input = True
            ip = input
            config_changed = True
        elif ip:
          valid_input = True
        if not valid_input:
          print "Invalid value. Please try again."
      print
  
      if netmask:
        str_to_print = "Enter netmask (currently %s, press enter to retain current value) : "%netmask
      else:
        str_to_print = "Enter netmask (currently not set) : "
      valid_input = False
      while not valid_input:
        input = raw_input(str_to_print)
        if input:
          ok, err = networking.validate_netmask(input)
          if err:
            raise Exception('Error validating netmask : %s'%err)
          if ok:
            valid_input = True
            netmask = input
            config_changed = True
        elif netmask:
          valid_input = True
        if not valid_input:
          print "Invalid value. Please try again."
      print

    if config_changed:
      d = {}
      d['addr_type'] = boot_proto
      if boot_proto == 'static':
        d['ip'] = ip
        d['netmask'] = netmask
      ret, err = networking.set_interface_ip_info(ifname, d)
      if not ret:
        if err:
          raise Exception('Error changing interface address : %s'%err)
        else:
          raise Exception('Error changing interface address')
  
      restart = False
      print
      print
      valid_input = False
      while not valid_input:
        str_to_print = 'Restart network services now (y/n) :'
        print
        input = raw_input(str_to_print)
        if input:
          if input.lower() in ['y', 'n']:
            valid_input = True
            if input.lower() == 'y':
              restart = True
        if not valid_input:
          print "Invalid value. Please try again."
      print
      if restart:
        r, rc = command.execute_with_rc('service network restart')
        if rc == 0:
          print "Network service restarted succesfully."
        else:
          print "Error restarting network services."
          raw_input('Press enter to return to the main menu')
          return -1
        r, rc = command.execute_with_rc('service salt-minion restart')
        if rc == 0:
          print "Salt minion service restarted succesfully."
        else:
          print "Error restarting salt minion services."
          raw_input('Press enter to return to the main menu')
          return -1
    else:
      print
      print
      raw_input('No changes have been made to the configurations. Press enter to return to the main menu.')
      return 0

  except Exception, e:
    print "Error configuring network settings : %s"%e
    return -1
  else:
    return 0


if __name__ == '__main__':

  #print sys.argv
  if len(sys.argv) != 2:
    print 'Incorrect usage. Usage : configure_networking interface|dns|gateway'
    sys.exit(-1)
  if sys.argv[1] not in ['interface']:
    print 'Incorrect usage. Usage : configure_networking interface|dns|gateway'
    sys.exit(-1)
  if sys.argv[1] == 'interface':
    rc = configure_interface()
  sys.exit(rc)

    
'''
def configure_networking():

  try :
    os.system('clear')
    change_ip = False
    change_netmask = False
    #change_hostname = False
    change_default_gateway = False
    change_dns_primary = False
    change_dns_secondary = False
    change_dns_external = False
    change_bonding_type = False
    change_jumbo_frames = False
  
    ip_info = networking.get_ip_info('bond0')
    if not ip_info :
      print "No bonding configured! Incorrect configuration. Please contact Fractalio Data"
      sys.exit(-1)
  
    config_changed = False
    ip = ip_info["ipaddr"]
    str_to_print = "Enter IP address (currently %s, press enter to retain current value) : "%ip
    valid_input = False
    while not valid_input :
      input = raw_input(str_to_print)
      if input:
        if networking.is_ip(input):
          valid_input = True
          ip = input
          change_ip = True
          config_changed = True
      else:
        valid_input = True
      if not valid_input:
        print "Invalid value. Please try again."
    print
  
    netmask = ip_info["netmask"]
    str_to_print = "Enter netmask (currently %s, press enter to retain current value) : "%netmask
    valid_input = False
    while not valid_input:
      input = raw_input(str_to_print)
      if input:
        if networking.is_ip(input):
          valid_input = True
          netmask = input
          change_netmask = True
          config_changed = True
      else:
        valid_input = True
      if not valid_input:
        print "Invalid value. Please try again."
    print
  
    hostname = socket.gethostname()
    if not hostname:
      str_to_print = "Enter hostname (currently no hostname configured, press enter to retain current value) : "
    else:
      str_to_print = "Enter hostname without any domain name (currently %s, press enter to retain current value) : "%hostname
    valid_input = False
    while not valid_input:
      input = raw_input(str_to_print)
      if input:
        if re.match('^[a-zA-Z0-9-]+$', input):
          valid_input = True
          hostname = input
          change_hostname = True
          config_changed = True
      else:
        valid_input = True
      if not valid_input:
        print "Invalid value. Please try again."
    print
  
    default_gateway = None
    if "default_gateway" in ip_info:
      default_gateway = ip_info["default_gateway"]
    else:
      default_gateway = None
    if default_gateway:
      str_to_print = "Enter the default gateway's IP address (currently %s, press enter to retain current value) : "%default_gateway
    else:
      str_to_print = "Enter the default gateway's IP address (currently not set, press enter to retain current value) : "
    valid_input = False
    while not valid_input:
      input = raw_input(str_to_print)
      if input:
        if networking.is_ip(input):
          valid_input = True
          default_gateway = input
          change_default_gateway = True
          config_changed = True
      else:
        valid_input = True
      if not valid_input:
        print "Invalid value. Please try again."
    print
  
    dns_list = networking.get_name_servers()
    dns_primary = None
    if not dns_list:
      str_to_print = "Enter the IP address of the Fractalio primary GRIDCell (currently not set, press enter to retain current value) : "
    else:
      dns_primary = dns_list[0]
      str_to_print = "Enter the IP address of the Fractalio primary GRIDCell (currently %s, press enter to retain current value) : "%dns_primary
    valid_input = False
    while not valid_input:
      input = raw_input(str_to_print)
      if input:
        if networking.is_ip(input):
          valid_input = True
          dns_primary = input
          change_dns_primary = True
          config_changed = True
      else:
        valid_input = True
      if not valid_input:
        print "Invalid value. Please try again."
    print
  
    dns_secondary = None
    if (not dns_list) or (len(dns_list) <= 1):
      str_to_print = "Enter the IP address of the Fractalio secondary GRIDCell (currently not set, press enter to retain current value) : "
    else:
      dns_secondary = dns_list[1]
      str_to_print = "Enter the IP address of the Fractalio secondary GRIDCell (currently %s, press enter to retain current value) : "%dns_secondary
    valid_input = False
    while not valid_input:
      input = raw_input(str_to_print)
      if input:
        if networking.is_ip(input):
          valid_input = True
          dns_secondary = input
          change_dns_secondary = True
          config_changed = True
      else:
        valid_input = True
      if not valid_input:
        print "Invalid value. Please try again."
    print
  
    dns_external = None
    if not dns_list:
      str_to_print = "Enter the IP address of the customer's DNS server (currently not set, press enter to retain current value) : "
    else:
      if len(dns_list) > 2:
        dns_external = dns_list[2]
      str_to_print = "Enter the IP address of the customer's DNS server (currently %s, press enter to retain current value) : "%dns_external
    valid_input = False
    while not valid_input:
      input = raw_input(str_to_print)
      if input:
        if networking.is_ip(input):
          valid_input = True
          dns_external = input
          change_dns_external = True
          config_changed = True
      else:
        valid_input = True
      if not valid_input:
        print "Invalid value. Please try again."
    print
  
    bonding_type = networking.get_bonding_type('bond0')
    print "Ethernet NIC bonding configuration"
    print "----------------------------------"
    print "Ethernet bonding aggregates the bandwidth of all available ethernet ports giving high throughput and failover."
    print "We support two modes. "
    print "The first is LACP (also called 802.3ad) which requires configuration on any switch). The second is balance-alb which does not require switch configuration but may not be supported on all switches. "
    valid_input = False
    while not valid_input:
      print "Valid choices for this selection  are 4 (for 802.3ad or LACP) and 6 (for balance-alb)."
      print
      if bonding_type == -1:
        str_to_print = "Enter bonding mode (currently not configured, press enter to retain current value) : "
      else:
        str_to_print = "Enter bonding mode (currently %s, press enter to retain current value) : "%bonding_type
      input = raw_input(str_to_print)
      if input:
        if input.lower() in ['4', '6']:
          valid_input = True
          bonding_type = int(input)
          change_bonding_type = True
          config_changed = True
      else:
        valid_input = True
      if not valid_input:
        print "Invalid value. Please try again."
    print
  
    
    jfe = networking.jumbo_frames_enabled('bond0')
    if jfe:
      jumbo_frames = 'y'
      jfe_str = "enabled"
    else:
      jumbo_frames = 'n'
      jfe_str = "disabled"
    print "Jumbo frames support"
    print "--------------------"
    print "Enabling jumbo frames improves network throughput but requires configuration on the switch side."
    print "If you enable it here, please set the MTU size on the switch to 9000"
    valid_input = False
    while not valid_input:
      str_to_print = "Enable jumbo frames (currently %s, press enter to retain current value) (y/n)? : "%jfe_str
      print
      input = raw_input(str_to_print)
      if input:
        if input.lower() in ['y', 'n']:
          valid_input = True
          jumbo_frames = input.lower()
          change_jumbo_frames = True
          config_changed = True
      else:
        valid_input = True
      if not valid_input:
        print "Invalid value. Please try again."
    print

    print "Final confirmation"
    print "------------------"
  
    print
    print "The following are the choices that you have made :"
    print "IP address : %s"%ip
    print "Net Mask : %s"%netmask
    #print "Hostname : %s"%hostname
    print "Default gateway : %s"%default_gateway
    print "IP address of the Fractalio primary GRIDCell : %s"%dns_primary
    print "IP address of the Fractalio secondary GRIDCell : %s"%dns_secondary
    print "IP address of the customer's DNS server: %s"%dns_external
    if bonding_type == 4:
      print "NIC Bonding mode : LACP"
    elif bonding_type == 6:
      print "NIC Bonding mode : balance-alb"
    else:
      print "NIC Bonding mode (unsupported!!) : %d"%bonding_type
  
    print "Enable jumbo frames : %s"%jumbo_frames
  
    if not config_changed:
      print
      print
      raw_input('No changes have been made to the configurations. Press enter to return to the main menu.')
      return 0

    str_to_print = 'Commit the above changes? (y/n) :'
      
    commit = 'n'
    valid_input = False
    while not valid_input:
      input = raw_input(str_to_print)
      if input:
        if input.lower() in ['y', 'n']:
          valid_input = True
          commit = input.lower()
      if not valid_input:
        print "Invalid value. Please try again."
    print
  
    if commit == 'y':
      print "Committing changes!"
    else:
      print "Discarding changes!"
  
    if commit != 'y':
      return 0
  
    restart_networking = False
    ip_dict = {}
    errors = []
    if change_ip or change_netmask or change_default_gateway or change_jumbo_frames:
      ip_dict["ip"] = ip
      ip_dict["netmask"] = netmask
      ip_dict["default_gateway"] = default_gateway
      if jumbo_frames == 'y':
        ip_dict["mtu"] = 9000
      else:
        ip_dict["mtu"] = 1500
      rc = networking.set_bond_ip_info(ip_dict)
      if rc == -1:
        errors.append("Error setting IP configuration")
      restart_networking = True
      #This is done to change the /etc/hosts file to the correct IP
      rc = networking.change_hosts_file_entry(hostname, ip_info['ipaddr'], hostname, ip)
      if rc == -1:
        errors.append("Error setting IP configuration")

    if change_hostname:
      rc = networking.set_hostname(hostname)
      if rc == -1:
        errors.append("Error setting hostname")
  
    if change_dns_primary or change_dns_secondary or change_dns_external: 
      fqdn = socket.getfqdn()
      if fqdn == 'fractalio-pri.fractalio.lan':
        if dns_external:
          rc = networking.generate_default_primary_named_conf(dns_primary, netmask, dns_secondary, True, dns_external, True)
        else:
          rc = networking.generate_default_primary_named_conf(dns_primary, netmask, dns_secondary)
        if rc == -1:
          errors.append("Error setting DNS server configuration")
      rc = networking.set_name_servers([dns_primary, dns_secondary, dns_external])
      if rc == -1:
        errors.append("Error setting name servers")
  
    if change_bonding_type:
      networking.set_bonding_type('bond0', bonding_type)
      if rc == -1:
        errors.append("Error setting bonding type")
      restart_networking = True
  
    restart = False
      print
      print
      valid_input = False
      while not valid_input:
        str_to_print = 'Restart network services now (y/n) :'
        print
        input = raw_input(str_to_print)
        if input:
          if input.lower() in ['y', 'n']:
            valid_input = True
            if input.lower() == 'y':
              restart = True
        if not valid_input:
          print "Invalid value. Please try again."
      print
    if restart:
      r, rc = command.execute_with_rc('service network restart')
      if rc == 0:
        print "Network service restarted succesfully."
      else:
        print "Error restarting network services."
        raw_input('Press enter to return to the main menu')
        return -1
      r, rc = command.execute_with_rc('service salt-minion restart')
      if rc == 0:
        print "Salt minion service restarted succesfully."
      else:
        print "Error restarting salt minion services."
        raw_input('Press enter to return to the main menu')
        return -1
      r, rc = command.execute_with_rc('service named restart')
      if rc == 0:
        print "DNS service restarted succesfully."
        raw_input('Press enter to return to the main menu')
        return 0
      else:
        print "Error restarting DNS services."
        raw_input('Press enter to return to the main menu')
        return -1
  except Exception, e:
    print "Error configuring network settings : %s"%e
    return -1
  else:
    return 0
'''
