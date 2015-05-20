import salt.client
import sys, os, pwd, crypt


import fractalio
from fractalio import command 

def create_local_user(userid, name, pswd):

  error_list = []
  #First check if samba user exists. if so kick out
  ul = get_local_users()
  if ul:
    for ud in ul:
      if ud["userid"] == userid:
        raise Exception("Error creating user. The user \"%s\" already exists. "%userid)

  # Now check if system user exists. If not create..
  create_system_user = False
  try:
    pwd.getpwnam(userid)
  except KeyError:
    create_system_user = True

  if create_system_user:
    #enc_pswd = crypt.crypt(pswd, "28")
    #Set a standard system password - not the one given by the user as the user should not have access to the system
    enc_pswd = crypt.crypt("fractal_pswd_%s"%userid, "28")
    client = salt.client.LocalClient()
    rc = client.cmd('*', 'user.add', [userid,None,501])
    for hostname, status in rc.items():
      if not status:
        error_list.append("Error creating the userid on GRIDCell %s"%hostname)
    rc = client.cmd('*', 'shadow.set_password', [userid, enc_pswd] )
    for hostname, status in rc.items():
      if not status:
        error_list.append("Error setting the password for userid on GRIDCell %s"%hostname)
    rc = client.cmd('*', 'user.chfullname', [userid, "fractal_user_%s"%name] )
    for hostname, status in rc.items():
      if not status:
        error_list.append("Error setting the name for userid on GRIDCell %s"%hostname)
    '''
    ret, rc = command.execute_with_rc(r'useradd -p %s -c fractal_user_%s %s'%(enc_pswd, name, userid))
    if rc != 0:
      raise Exception("Error creating system user. Return code : %d. "%rc)
    '''

  # Now all set to create samba user
  ret, rc = command.execute_with_conf_and_rc(r'/usr/bin/pdbedit  -d 1 -t -a  -u %s -f %s'%(userid, name), "%s\n%s"%(pswd, pswd))
  if rc != 0:
    #print command.get_error_list(ret)
    raise Exception("Error creating user. Return code : %d. "%rc)
  ul = command.get_output_list(ret)
  #print ul
  return error_list


def delete_local_user(userid):

  error_list = []
  #First check if samba user exists. if so kick out
  ul = get_local_users()
  found = False
  if ul:
    for ud in ul:
      if ud["userid"] == userid:
        found = True
  if not found:
    raise Exception("Error deleting user. The user \"%s\" does not exist. "%userid)

  # Now check if system user exists. If so and is created by fractal then delete..
  delete_system_user = False
  try:
    d = pwd.getpwnam(userid)
    name = d[4]
    if name.find("fractal_user") == 0:
      delete_system_user = True
  except KeyError:
    pass

  if delete_system_user:
    '''
    #print "Deleting user %s from the system"%userid
    ret, rc = command.execute_with_rc(r'userdel %s'%userid)
    if rc != 0:
      raise Exception("Error deleting user from the underlying system. Return code : %d. "%rc)
    #print "Deleted user %s from the system"%userid
    '''
    client = salt.client.LocalClient()
    rc = client.cmd('*', 'user.delete', [userid] )
    for hostname, status in rc.items():
      if not status:
        error_list.append("Error deleting the userid on GRIDCell %s"%hostname)

  #print "Deleting user %s from the storage system"%userid
  ret, rc = command.execute_with_rc(r'pdbedit -d 1 -x %s'%userid)
  if rc != 0:
    raise Exception("Error deleting user from the storage system. Return code : %d. "%rc)
  #print "Deleted user %s from the storage system"%userid
  return error_list



def change_password(userid, pswd):
  ret, rc = command.execute_with_conf_and_rc(r'smbpasswd -s %s'%(userid), "%s\n%s"%(pswd, pswd))
  if rc != 0:
    print ret
    #print command.get_error_list(ret)
    raise Exception("Error changing password. Return code : %d. "%rc)
  ul = command.get_output_list(ret)
  #print ul

def get_local_users():
  print "Comes Here"
  ret, rc = command.execute_with_rc("/usr/bin/pdbedit -d 1 -L")
  print ret
  if rc != 0:
    raise "Error retrieving user list. Return code : %d"%rc

  ul = command.get_output_list(ret)
  user_list = []
  for u in ul:
    l = u.split(':')
    if l:
      d = {}
      d["userid"] = l[0]
      if len(l) > 1:
        d["name"] = l[2]
      user_list.append(d)
  print user_list
  return user_list

def main():
  #change_password("bkrram", "ram1")
  delete_local_user("ram2")
  #print get_samba_users()

if __name__ == "__main__":
  main()

