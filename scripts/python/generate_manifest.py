#!/usr/bin/python

import json, os, datetime, shutil, sys
from integralstor_common import lock, common
from integralstor_unicell import manifest_status

def gen_manifest(path):
  try:
    if not lock.get_lock('generate_manifest'):
      raise Exception('Could not acquire lock.')
    ret, err = manifest_status.generate_manifest_info()
    if not ret :
      if err:
        raise Exception(err)
      else:
        raise Exception('No manifest info obtained')
    else:
      fullpath = os.path.normpath("%s/master.manifest"%path)
      fulltmppath = os.path.normpath("%s/master.manifest.tmp"%path)
      fullcopypath = os.path.normpath("%s/master.manifest.%s"%(path, datetime.datetime.now().strftime("%B_%d_%Y_%H_%M_%S")))
      #Generate into a tmp file
      with open(fulltmppath, 'w') as fd:
        json.dump(ret, fd, indent=2)
      #Copy original to a backup
      if os.path.isfile(fullpath):
        shutil.copyfile(fullpath, fullcopypath)
      #Now move the tmp to the actual manifest file name
      shutil.move(fulltmppath, fullpath)
  except Exception, e:
    print 'Error generating manifest : %s'%str(e)
    lock.release_lock('generate_manifest')
    return -1
  else:
    lock.release_lock('generate_manifest')
    return 0

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
