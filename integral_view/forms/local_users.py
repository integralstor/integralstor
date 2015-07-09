import salt.client
import sys, os, pwd, crypt, grp


import integralstor_common
from integralstor_common import command 

def create_local_user(username, name, pswd, smb_user=False):

  try:

    #First check if user exists. if so kick out
    ul, err = get_local_users()
    if ul:
      for ud in ul:
        if ud["username"] == username:
          raise Exception("Error creating user. The user \"%s\" already exists. "%username)
    elif not err:
      raise Exception("Error retrieving user list : %s"%err)

  
    enc_pswd = crypt.crypt(pswd, "28")
    client = salt.client.LocalClient()
    rc = client.cmd('*', 'user.add', [username])
    for hostname, status in rc.items():
      if not status:
        error_list.append("Error creating the username on node"%hostname)
    rc = client.cmd('*', 'shadow.set_password', [username, enc_pswd] )
    for hostname, status in rc.items():
      if not status:
        error_list.append("Error setting the password for username on GRIDCell %s"%hostname)
    rc = client.cmd('*', 'user.chfullname', [username, "integralstor_user_%s"%name] )
    for hostname, status in rc.items():
      if not status:
        error_list.append("Error setting the name for username on node %s"%hostname)
    '''
    ret, rc = command.execute_with_rc(r'useradd -p %s -c integralstor_user_%s %s'%(enc_pswd, name, username))
    if rc != 0:
      raise Exception("Error creating system user. Return code : %d. "%rc)
    '''
  
    if smb_user:
      print '/usr/bin/pdbedit  -d 1 -t -a  -u %s -f %s'%(username, name), "%s\n%s"%(pswd, pswd)
      # Now all set to create samba user
      ret, rc = command.execute_with_conf_and_rc(r'/usr/bin/pdbedit  -d 1 -t -a  -u %s -f %s'%(username, name), "%s\n%s"%(pswd, pswd))
      if rc != 0:
        #print command.get_error_list(ret)
        print ret, rc
        raise Exception("Error creating user's CIFS access. Return code : %d. "%rc)
      #ul = command.get_output_list(ret)
      #print ul
  except Exception, e:
    return False, 'Error creating local user : %s'%str(e)
  else:
    return True, None


def create_local_group(group_name, gid = None):
  try:
    client = salt.client.LocalClient()
    rc = client.cmd('*', 'group.add', [group_name,gid])
    for hostname, status in rc.items():
      if not status:
        raise Exception('Group creation failed')
  except Exception, e:
    return False, 'Error creating a local group : %s'%str(e)
  else:
    return True, None

def delete_local_user(username):

  try:
    if not username:
      raise Exception('No username specified')
    d, err = get_local_user(username)
    if not d:
      if err:
        raise Exception('Error locating user : %s'%err)
      else:
        raise Exception('Error locating user')

    client = salt.client.LocalClient()
    rc = client.cmd('*', 'user.delete', [username] )
    print rc
    if rc:
      for hostname, status in rc.items():
        if not status:
          raise Exception("Error deleting the system user")
    else:
          raise Exception("Error deleting the system user")
    if d['smb_user']:
      ret, rc = command.execute_with_rc(r'pdbedit -d 1 -x %s'%username)
      if rc != 0:
        raise Exception("Error deleting user from the cifs storage system. Return code : %d. "%rc)
    
  except Exception, e:
    return False, 'Error deleting local user : %s'%str(e)
  else:
    return True, None




def change_password(username, pswd):
  try:
    if not username:
      raise Exception('No username specified')
    d, err = get_local_user(username)
    if not d:
      if err:
        raise Exception('Error locating user : %s'%err)
      else:
        raise Exception('Error locating user')
    ret, rc = command.execute_with_conf_and_rc(r'echo \"%s:%s\"|chpasswd'%(username, pswd))
    if rc != 0:
      print ret
      #print command.get_error_list(ret)
      raise Exception("Error changing system password.")

    if 'smb_user' in d and d['smb_user']:
      ul = command.get_output_list(ret)
      ret, rc = command.execute_with_conf_and_rc(r'smbpasswd -s %s'%(username), "%s\n%s"%(pswd, pswd))
      if rc != 0:
        print ret
        #print command.get_error_list(ret)
        #ul = command.get_output_list(ret)
        raise Exception("Error changing CIFS password. Return code : %d. "%rc)
  except Exception, e:
    return False, 'Error changing local user password : %s'%str(e)
  else:
    return True, None

  ret, rc = command.execute_with_conf_and_rc(r'smbpasswd -s %s'%(userid), "%s\n%s"%(pswd, pswd))
  if rc != 0:
    print ret
    #print command.get_error_list(ret)
    raise Exception("Error changing password. Return code : %d. "%rc)
  ul = command.get_output_list(ret)
  #print ul

def get_local_user(username, user_list = None):
  ret = None
  try:
    if not username:
      raise Exception('No username specified')
    if not user_list:
      user_list, err = get_local_users()
    if not user_list :
      if err:
        raise Exception('Error retrieving user list : %s'%err)
      else:
        raise Exception('Specified user not found')
    for ud in user_list:
      if ud['username'] == username:
        ret = ud
        break
  except Exception, e:
    return None, 'Error retrieving local user : %s'%str(e)
  else:
    return ret, None

def get_local_users():
  user_list = []
  try:
    sys_ul = []
    smb_ul = []
    all = pwd.getpwall()
    for user in all:
      if user[2] < 500:
        continue
      sys_ul.append(user[1])
      d = {}
      d['uid'] = user[2]
      d['gid'] = user[3]
      d['home_dir'] = user[5]
      d['username'] = user[0]
      d['comment'] = user[4]
      user_list.append(d)
    ret, rc = command.execute_with_rc("/usr/bin/pdbedit -d 1 -L")
    if rc != 0:
      raise "Error retrieving user list. Return code : %d"%rc

    ul = command.get_output_list(ret)
    smb_ul = []
    smb_dict = {}
    for u in ul:
      l = u.split(':')
      if l:
        if len(l) > 1:
          smb_dict['name'] = l[2]
        smb_ul.append(l[0])
    for ud in user_list:
      if ud['username'] in smb_ul:
        ud['smb_user'] = True
        if ud['username'] in smb_dict:
          ud['smb_comment'] = smb_dict[u['username']]
      else:
        ud['smb_user'] = True
        ud['smb_user'] = False
  except Exception, e:
    None, 'Error retrieving local users : %s'%str(e)
  else:
    return user_list, None


def main():
  #change_password("bkrram", "ram1")
  #delete_local_user("ram2")
  #print get_samba_users()
  print get_local_users()

if __name__ == "__main__":
  main()

'''
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

  # Now check if system user exists. If so and is created by integralstor then delete..
  delete_system_user = False
  try:
    d = pwd.getpwnam(userid)
    name = d[4]
    if name.find("integralstor_user") == 0:
      delete_system_user = True
  except KeyError:
    pass

  if delete_system_user:
    #print "Deleting user %s from the system"%userid
    ret, rc = command.execute_with_rc(r'userdel %s'%userid)
    if rc != 0:
      raise Exception("Error deleting user from the underlying system. Return code : %d. "%rc)
    #print "Deleted user %s from the system"%userid
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
'''
