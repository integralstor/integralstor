import pprint

from integralstor_unicell import manifest_status

def disk_info_and_status():

  disks, err = manifest_status.disk_info_and_status()
  return disks
    
    
def pool_status():
  pools, err = manifest_status.pool_status()
  return pools

def interface_status():
  int_status, err = manifest_status.interface_status()
  return int_status
   
def load_avg():
  lavg, err = manifest_status.load_avg()
  return lavg

def mem_info():
  meminfo, err = manifest_status.mem_info()
  return meminfo


def ipmi_status():
  ipmi, err = manifest_status.ipmi_status()
  return ipmi

def status():
  sd, err = manifest_status.status()
  return sd
      
if __name__ == '__main__':
  #print status()
  #print status()
  #print _diskmap()
  pp = pprint.PrettyPrinter(indent=4)
  #pp.pprint(disk_info_and_status())
  #d = pool_status()
  #pp.pprint(d)
  #pp.pprint(d)
  #print disk_status()
  pp.pprint(interface_status())
  #print status()
  #print load_avg()
  #print disk_usage()
  #print mem_info()
