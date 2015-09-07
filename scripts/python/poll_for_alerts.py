#!/usr/bin/python
import sys, time

import integralstor_common
from integralstor_common import common, alerts, lock, command
from integralstor_unicell import lcd_display, system_info


import atexit
atexit.register(lock.release_lock, 'poll_for_alerts')

def node_up(node):
    # Check node status
    if "node_status" in node:
      if node["node_status"] != 0:
        if node["node_status"] < 0:
          return False 
    return True

def check_disk_status(node, node_name):

  alert_list = []
  try: 
    python_scripts_path, err = common.get_python_scripts_path()
    if err:
      raise Exception(err)
    err_pos = []
    s = ""
    if "disks" in node:
      disks = node["disks"]
      for sn, disk in disks.items():
        if "status" in disk and disk["status"] != 'PASSED':
          alert_list.append("Disk with serial number %s has problems."%(sn))
          err_pos.append(disk["position"])
    if err_pos:
      i = 1
      while i < 5:
        if i in err_pos:
          s += "Err"
        else:
          s += "Ok"
        if i < 4:
          s += ' '
        i += 1
      s1 =  '%s/lcdmsg.py "Disk error slots" "%s"'%(python_scripts_path, s)
    else:
      s1 =  '%s/lcdmsg.py "Integral-stor" "Unicell"'%python_scripts_path
    (ret, rc), err = command.execute_with_rc(s1)
    if err:
      raise Exception(err)
  except Exception, e:
    return None, 'Error checking disk status : %s'%str(e)
  else:
    return alert_list, None


def check_ipmi_status(node, node_name):

  alert_list = []
  try:
    if "ipmi_status" in node:
      status_list = node["ipmi_status"]
      for status_item in status_list:
        if status_item["status"] != 'ok':
          m = "The %s of the %s is reporting errors" %(status_item["parameter_name"], status_item["component_name"])
          if "reading" in status_item:
            m += " with a reading of %s."%status_item["reading"]
          alert_list.append(m)
  except Exception, e:
    return None, 'Error checking ipmi status : %s'%str(e)
  else:
    return alert_list, None

def check_interface_status(node, node_name):

  alert_list = []
  try:
    if "interfaces" in node:
      interfaces = node["interfaces"]
      for if_name, interface in interfaces.items():
        if 'lo' in if_name:
          continue
        print if_name, interface
        if "status" in interface and interface["status"] != 'up':
          alert_list.append("The network interface %s has problems."%(if_name))
  except Exception, e:
    return None, 'Error checking interface status : %s'%str(e)
  else:
    return alert_list, None

def check_pool_status(node, node_name):

  alert_list = []
  try:
    if "pools" in node:
      pools = node["pools"]
      for pool in pools:
        pool_name = pool['pool_name']
        if pool['config']['pool']['root']['status']["state"] != 'ONLINE':
          alert_list.append( "The ZFS pool %s has issues. Pool state is %s"%(pool_name, pool["state"]))
        '''
        if "raid_or_mirror_status" in pool["config"]:
          if pool["config"]["raid_or_mirror_status"]["state"] != 'ONLINE':
            alert_list.append( "The RAIDZ status ZFS pool %s on GRIDCell %s has issues. The RAIDZ state is %s"%(pool_name, node_name, pool["config"]["raid_or_mirror_status"]["state"]))
        '''
        if "components" in pool["config"]['pool']:
          for cname, component in pool["config"]['pool']["components"].items():
            if component["state"] != 'ONLINE':
              alert_list.append( "The component %s in the ZFS pool %s has issues. Component state is %s"%(component["name"], pool_name, component["state"]))
  except Exception, e:
    return None, 'Error checking pool status : %s'%str(e)
  else:
    return alert_list, None


def check_load_average(node, node_name):

  alert_list = []
  try:
    if "load_avg" in node:
      if node["load_avg"]["5_min"] > node["load_avg"]["cpu_cores"]:
        alert_list.append("The 5 minute load average has been high with a value of %.2f."%(node["load_avg"]["5_min"]))
      if node["load_avg"]["15_min"] > node["load_avg"]["cpu_cores"]:
        alert_list.append("The 15 minute load average on has been high with a value of %.2f."%(node["load_avg"]["15_min"]))
  except Exception, e:
    return None, 'Error checking pool status : %s'%str(e)
  else:
    return alert_list, None


def main():


  try :
    lck, err = lock.get_lock('poll_for_alerts')
    if err:
      raise Exception(err)
    if not lck:
      raise Exception('Could not acquire lock. Exiting.')
    si, err = system_info.load_system_config()
    if err:
      raise Exception(err)
    if not si:
      raise Exception('Could not load system information')
    alert_list = []
  
    for node_name, node in si.items():
  
      if not node_up(node):
        alert_list.append("GRIDCell %s seems to be down."%node_name)
  
      # Check disks status
      l, err = check_disk_status(node, node_name)
      if err:
        print 'Error generating disk status : %s'%err
      if l:
        alert_list.extend(l)
      
  
      # Check ipmi status
      l, err = check_ipmi_status(node, node_name)
      if err:
        print 'Error generating ipmi status : %s'%err
      if l:
        alert_list.extend(l)
  
      # Check interface status
      l, err = check_interface_status(node, node_name)
      if err:
        print 'Error generating interface status : %s'%err
      if l:
        alert_list.extend(l)
  
      # Check zfs pool status
      l, err = check_pool_status(node, node_name)
      if err:
        print 'Error generating pool status : %s'%err
      if l:
        alert_list.extend(l)
  
      # Check load average
      min = time.localtime().tm_min
      if min%15 == 0:
        l, err = check_load_average(node, node_name)
        if err:
          print 'Error generating load average status : %s'%err
        if l:
          alert_list.extend(l)

  
    #print alert_list
    print alert_list
    if alert_list:
      alerts.raise_alert(alert_list)
    lock.release_lock('poll_for_alerts')
  except Exception, e:
    print "Error generating alerts : %s ! Exiting."%str(e)
    sys.exit(-1)
  else:
    sys.exit(0)

if __name__ == "__main__":
  main()


'''
    print node
    if node["node_status"] != 0:
      if node["node_status"] == -1:
        alerts.raise_alert(alert_url, 'GRIDCell %s seems to be down. View the \"System status\" screen for more info.'%(name))
      elif node["node_status"] > 0:
        raise_alert(alert_url, 'Node %s seems to be degraded with the following errors : %s.'%(name, ' '.join(node["errors"])))
    if node["cpu_status"]["status"] != "ok":
      alerts.raise_alert(alert_url, 'The CPU on GRIDCell %s has issues. View the \"System status\" screen for more info.'%(name))
    if "ipmi_status" in node:        
      for status_dict in node["ipmi_status"]:
        if status_dict["status"] != "ok":
          alerts.raise_alert(alert_url, 'The %s on GRIDCell %s has issues. The %s shows a value of %s. View the \"System status\" screen for more info.'%(status_dict["component_name"], status_dict["parameter_name"], status_dict["reading"]))
    for n, v in node["disk_status"].items():
      if v["status"] != "PASSED":
        alerts.raise_alert(alert_url, 'Disk %s on GRIDCell %s has issues. View the \"System status\" screen for more info.'%(n, name))
  sd = system_info.get_chassis_components_status(settings.PRODUCTION)

  if sd:
    for fan in sd["fans"]:
      if "status" in fan and fan["status"] != "ok":
        if fan["name"] in ["Fan_SYS3_1", "Fan_SYS3_2"]:
          raise_alert(alert_url, 'Power supply fan %s not functioning. View the back panel tab on the \"System status\" screen to get a visual picture of the failure.'%fan["name"])
        else:
          raise_alert(alert_url, 'Fan %s not functioning. View the back panel tab on the \"System status\" screen  to get a visual picture of the failure.'%fan["name"])
    for ps in sd["psus"]:
      if "status" in ps and ps["status"] != "ok":
        raise_alert(alert_url, 'Power supply unit %s not functioning. View the front panel tab on the \"System status\" screen  to get a visual picture of the failure.'%psu["name"])
      if "code" in ps and ps["code"] == '0x09':
        raise_alert(alert_url, 'No input to power supply unit %s. View the front panel tab on the \"System status\" screen to get a visual picture of the failure.'%ps["name"])
'''
