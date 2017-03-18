#!/usr/bin/python
import sys
from integralstor_common import remote_replication, zfs
from datetime import datetime

def add_remote_replication_task(source_dataset, destination_ip, destination_username, destination_pool):
  try:
    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d-%H-%M')
    ret, err = zfs.create_snapshot(source_dataset, 'remote_repl_snap_%s'%now_str)
    description = 'Replication of %s to pool %s on machine %s'%(source_dataset, destination_pool, destination_ip)
    ret, err = remote_replication.schedule_remote_replication(description, source_dataset, destination_ip, destination_username, destination_pool)
    if err:
      raise Exception(err)
  except Exception, e:
    return False, 'Error adding a remote replication task : %s'%e
  else:
    return True, None

if __name__ == '__main__':
  #print sys.argv
  if len(sys.argv) != 5 :
    print 'Usage : python add_remote_replication_task source_dataset destination_ip destination_username destination_pool'
    sys.exit(-1)
  ret, err = add_remote_replication_task(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])  
  if err:
    print err
    sys.exit(-1)
  sys.exit(0)

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
