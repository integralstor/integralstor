
from integralstor_common import networking, command
import os, socket, sys

from integralstor_common import common

def display_status():

  try :
    hostname = socket.gethostname()
    if common.use_salt():
      print "Salt master service status :",
      r, rc = command.execute_with_rc('service salt-master status')
      l = command.get_output_list(r)
      if l:
        print '\n'.join(l)
      else:
        l = command.get_error_list(r)
        if l:
          print '\n'.join(l)
      print "Salt minion service status :",
      r, rc = command.execute_with_rc('service salt-minion status')
      l = command.get_output_list(r)
      if l:
        print '\n'.join(l)
      else:
        l = command.get_error_list(r)
        print l
        if l:
          print '\n'.join(l)
    print "Samba service status :",
    r, rc = command.execute_with_rc('service smb status')
    l = command.get_output_list(r)
    if l:
      print '\n'.join(l)
    else:
      l = command.get_error_list(r)
      if l:
        print '\n'.join(l)
    print "Winbind service status :",
    r, rc = command.execute_with_rc('service winbind status')
    l = command.get_output_list(r)
    if l:
      print '\n'.join(l)
    else:
      l = command.get_error_list(r)
      if l:
        print '\n'.join(l)
  except Exception, e:
    print "Error displaying system status : %s"%e
    return -1
  else:
    return 0

if __name__ == '__main__':

  os.system('clear')
  print
  print
  print
  print "Integralstor Unicell configuration"
  print "----------------------------------"
  rc = display_status()
  print
  print
  #sys.exit(rc)

