import os, re, subprocess, glob, pprint

import salt.modules.network, salt.modules.ps, salt.modules.status
import fractalio
from integralstor_common import zfs, command, disks, hardware_utils


def process_call(command):
  process = subprocess.Popen(command, stdout=subprocess.PIPE)
  output = ""
  while True:
    out = process.stdout.readline()
    if out == '' and process.poll() != None: break
    output += out
  return (process.returncode, output)

def get_hdparm(devpath):
  argv = []
  argv.append("/sbin/hdparm")
  argv.append("-i")
  argv.append(devpath)

  return process_call(argv)

def get_serialno(output):
  for line in output.split():
    if "SerialNo" in line:
      return line.split('=')[1]


def _execute_command(command = None):
  """ This function executes a command and returns the output in the form of a tuple.
      Exits in the case of an exception.
  """

  if command is None:
    return None

  err = ''
  args = command.split()
  try:
    proc = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    if proc:
			ret = proc.communicate()

  except Exception as e:
    err = str(e)
    return err, None

  if ret:
    return ret, proc.returncode
  else:
    return ret, None


def _validate_cmd_output(output_tuple = None):

  if output_tuple is None:
    return None

  if output_tuple[0]  :
    output = output_tuple[0]
  else:
    print "Error : %s" % output_tuple[1]
    return None

  return output

def disk_info_and_status():

  hardware_utils.rescan_drives()
  all_disks, err = disks.get_disk_info_all()
  if not disks:
    return None

  pool_list, err = zfs.get_pools()
  if pool_list:
    for sn, disk in all_disks.items():
      id = disk['id']
      found = False
      for pool in pool_list:
        if 'config' in pool and pool['config']:
         for sname, section in pool['config'].items():
          if not section:
            continue
          if ('components' not in section) or (not section['components']):
            continue
          for cname, component in section['components'].items():
            if 'type' in component and component['type'] == 'device' and component['name'] == id:
              disk['pool'] = pool['pool_name']
              found = True
              break
          if found:
            break
        if found:
          break
  return all_disks
    
def pool_status():
  pl, err = zfs.get_pools()
  return pl

def interface_status():
  return salt.modules.network.interfaces()
   
def load_avg():
  d = salt.modules.status.loadavg()
  d["cpu_cores"] = int(_cpu_cores())
  return d

def disk_usage():
  return salt.modules.status.diskusage()

def _cpu_cores():
  d = salt.modules.status.cpuinfo()
  if d:
    return d["cpu cores"]
  else:
    return -1

def mem_info():
  d = salt.modules.status.meminfo()
  ret = {}
  if d:
    if "MemTotal" in d:
      ret['mem_total'] = d['MemTotal']
    if "MemFree" in d:
      ret['mem_free'] = d['MemFree']
  return ret


def ipmi_status():
  fil = os.popen("ipmitool sdr")
  str4 = fil.read()
  lines = re.split("\r?\n", str4)
  ipmi_status = []
  for line in lines:
    l = line.rstrip()
    if not l:
      continue
    #print l
    comp_list = l.split('|')
    comp = comp_list[0].strip()
    status = comp_list[2].strip()
    if comp in["CPU Temp", "System Temp", "DIMMA1 Temp", "DIMMA2 Temp", "DIMMA3 Temp", "FAN1", "FAN2", "FAN3"] and status != "ns":
      td = {}
      td["reading"] = comp_list[1].strip()
      td["status"] = comp_list[2].strip()
      if comp == "CPU Temp":
        td["parameter_name"] = "CPU Temperature"
        td["component_name"] = "CPU"
      elif comp == "System Temp":
        td["parameter_name"] = "System Temperature"
        td["component_name"] = "System"
      elif comp == "DIMMA1 Temp":
        td["parameter_name"] = "Memory card 1 temperature"
        td["component_name"] = "Memory card 1"
      elif comp == "DIMMA2 Temp":
        td["parameter_name"] = "Memory card 2 temperature"
        td["component_name"] = "Memory card 2"
      elif comp == "DIMMA3 Temp":
        td["parameter_name"] = "Memory card 3 temperature"
        td["component_name"] = "Memory card 3"
      elif comp == "FAN1":
        td["parameter_name"] = "Fan 1 speed"
        td["component_name"] = "Fan 1"
      elif comp == "FAN2":
        td["parameter_name"] = "Fan 2 speed"
        td["component_name"] = "Fan 2"
      elif comp == "FAN3":
        td["parameter_name"] = "Fan 3 speed"
        td["component_name"] = "Fan 3"
      ipmi_status.append(td)
  return ipmi_status

def status():
  d = {}
  d["disks"] = disk_info_and_status()
  d["interfaces"] = interface_status()
  d["pools"] = pool_status()
  d["load_avg"] = load_avg()
  #d["disk_usage"] = disk_usage()
  d["mem_info"] = mem_info()
  d["ipmi_status"] = ipmi_status()
  return d
      
if __name__ == '__main__':
  #print status()
  #print status()
  #print _diskmap()
  pp = pprint.PrettyPrinter(indent=4)
  #pp.pprint(disk_info_and_status())
  d = pool_status()
  pp.pprint(d)
  #pp.pprint(d)
  #print disk_status()
  #print interface_status()
  #print status()
  #print load_avg()
  #print disk_usage()
  #print mem_info()
