#!/usr/bin/python

import salt.client
import json, os, datetime, shutil, sys
from integralstor_common import lock, common
import pprint

def _gen_manifest_info():
  local = salt.client.LocalClient()
  data = local.cmd('*', 'grains.item', ['hwaddr_interfaces', 'mem_total', 'fqdn', 'cpu_model', 'roles'])
  dd = local.cmd('*', 'integralstor.disk_info_and_status')
  for node, diskinfo in dd.items():
    data[node]["disks"] = diskinfo
  #print data
  #print "disk info"
  #print dd
  pp = pprint.PrettyPrinter(indent=4)
  #pp.pprint(data)
  #print data
  if not data:
    print "Error getting grains"
    return -1, None
  ret = {}
  for k, v in data.items():
    #print k
    v['interfaces'] = {}
    #Tweak the key names
    if v and 'hwaddr_interfaces' in v and v['hwaddr_interfaces'] :
      for int_name, mac_addr in v['hwaddr_interfaces'].items():
        d = {}
        d['mac_addr'] = mac_addr
        '''
        if 'ip_interfaces' in v and int_name in v['ip_interfaces']:
          d['ip_addr'] = v['ip_interfaces'][int_name]
        else:
          d['ip_addr'] = []
        '''
        v['interfaces'][int_name] = d 

      v.pop('hwaddr_interfaces', None)
      #v.pop('ip_interfaces', None)
    ret[k] = v
    #print ret
  return 0, ret

def gen_manifest(path):
  if not lock.get_lock('generate_manifest'):
    print 'Generate Status : Could not acquire lock. Exiting.'
    return -1
  ret_code = 0
  rc, ret = _gen_manifest_info()
  if rc != 0 :
    ret_code = rc
  else:
    fullpath = os.path.normpath("%s/master.manifest"%path)
    fulltmppath = os.path.normpath("%s/master.manifest.tmp"%path)
    fullcopypath = os.path.normpath("%s/master.manifest.%s"%(path, datetime.datetime.now().strftime("%B_%d_%Y_%H_%M_%S")))
    try:
      #Generate into a tmp file
      with open(fulltmppath, 'w') as fd:
        json.dump(ret, fd, indent=2)
      #Copy original to a backup
      if os.path.isfile(fullpath):
        shutil.copyfile(fullpath, fullcopypath)
      #Now move the tmp to the actual manifest file name
      shutil.move(fulltmppath, fullpath)
    except Exception, e:
      print "Error generating the manifest file : %s"%str(e)
      ret_code = -1
  lock.release_lock('generate_manifest')
  return ret_code

import atexit
atexit.register(lock.release_lock, 'generate_manifest')

def main():

  try :
    num_args = len(sys.argv)
    if num_args > 1:
      path = sys.argv[1]
    else:
      path = common.get_system_status_path()
      if not path:
        path = '/tmp'
    print "Generating the manifest in %s"%path
    rc = gen_manifest(path)
    print rc
  except Exception, e:
    print "Error generating manifest file : %s"%e
    return -1
  else:
    return 0

if __name__ == "__main__":
  ret = main()
  sys.exit(ret)
