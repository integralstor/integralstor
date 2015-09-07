#!/usr/bin/python

from integralstor_unicell import manifest_status
from integralstor_common import lock, common
import json, os, shutil, datetime, sys, re
import pprint

  
def gen_status(path):
  try :
    lck, err = lock.get_lock('generate_status')
    if err:
      raise Exception(err)
    if not lck:
      raise Exception('Generate Status : Could not acquire lock.')
    fullmanifestpath = os.path.normpath("%s/master.manifest"%path)
    ret, err = manifest_status.generate_status_info(fullmanifestpath)
    if not ret :
      if err:
        raise Exception(err)
      else:
        raise Exception('No status info obtained')
    fullpath = os.path.normpath("%s/master.status"%path)
    fulltmppath = os.path.normpath("%s/master.status.tmp"%path)
    #Generate into a tmp file
    with open(fulltmppath, 'w') as fd:
      json.dump(ret, fd, indent=2)
    #Now move the tmp to the actual manifest file name
    shutil.move(fulltmppath, fullpath)
  except Exception, e:
    lock.release_lock('generate_status')
    return -1,  'Error generating status : %s'%str(e)
  else:
    lock.release_lock('generate_status')
    return 0, None

import atexit
atexit.register(lock.release_lock, 'generate_status')

def main():

    try :
      num_args = len(sys.argv)
      if num_args > 1:
        path = sys.argv[1]
      else:
        path, err = common.get_system_status_path()
        if err:
          raise Exception(err)
        if not path:
          path = '/tmp'
      print "Generating the status in %s"%path
      rc, err = gen_status(path)
      if err:
        raise Exception(err)
      print rc
    except Exception, e:
      print "Error generating status file : %s"%e
      return -1
    else:
      return 0


if __name__ == "__main__":
  main()
