#!/usr/bin/python
import sys, time

from integralstor_common import common, alerts, lock, db

import atexit, time, datetime
atexit.register (lock.release_lock, 'unicell_poll_for_alerts')

def main ():
  try :
    lck, err = lock.get_lock ('unicell_poll_for_alerts')
    if err:
      raise Exception(err)
    if not lck:
      raise Exception ('Could not acquire lock. Exiting.')
    
    alert_list = []
    now = int (time.time ())

    db_path, err = common.get_db_path ()    
    if err:
      raise Exception (err)

    tasks_query = "select * from tasks where last_run_time > '%d' and (status = 'error-retrying' or status = 'failed');" %(now-110)
    #print "\ntasks_query: ", tasks_query
    rows, err = db.read_multiple_rows (db_path, tasks_query)
    #print "\nrows: ", rows
    if err:
      raise Exception (err)
    
    if rows:
      for row in rows:
        msg = "%s: %s." %(row['status'], row['description']) 
        alert_list.append (msg)

    #print "\nalert_list: ", alert_list
    if alert_list:
      alerts.raise_alert (alert_list)

    lock.release_lock ('unicell_poll_for_alerts')

  except Exception, e:
    print "Error generating alerts : %s ! Exiting."%str(e)
    sys.exit(-1)
  else:
    sys.exit(0)

if __name__ == "__main__":
  main()


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
