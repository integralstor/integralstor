import salt.client
import sys, os, pwd, crypt, grp, spwd


import integralstor_common
from integralstor_common import command, common

def create_local_user(username, name, pswd, gid = None, smb_user=True):

  try:

    #First check if user exists. if so kick out
    ul, err = get_local_users()
    if ul:
      for ud in ul:
        if ud["username"] == username:
          raise Exception("Error creating user. The user \"%s\" already exists. "%username)
    elif err:
      raise Exception("Error retrieving user list : %s"%err)

  
    enc_pswd = crypt.crypt(pswd, "28")
    use_salt, err = common.use_salt()
    if err:
      raise Exception(err)
    if use_salt:
      client = salt.client.LocalClient()
      if gid:
        rc = client.cmd('*', 'user.add', [username, None, gid])
      else:
        rc = client.cmd('*', 'user.add', [username])
      #print rc
      if not rc:
        error_list.append("Error creating the username")
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
    else:
      if gid:
        cmd_to_run = 'useradd -g %s -p %s -c integralstor_user_%s %s'%(gid, enc_pswd, name, username)
      else:
        cmd_to_run = 'useradd  -p %s -c integralstor_user_%s %s'%(enc_pswd, name, username)
      (ret, rc), err = command.execute_with_rc(cmd_to_run)
      if err:
        raise Exception(err)
      if rc != 0:
        err = ''
        tl, er = command.get_output_list(ret)
        if er:
          raise Exception(er)
        if tl:
          err = ','.join(tl)
        tl, er = command.get_error_list(ret)
        if er:
          raise Exception(er)
        if tl:
          err = err + ','.join(tl)
        raise Exception("Return code : %d. Error : %s"%(rc, err))
  
    if smb_user:
      #print '/usr/bin/pdbedit  -d 1 -t -a  -u %s -f %s'%(username, name), "%s\n%s"%(pswd, pswd)
      # Now all set to create samba user
      (ret, rc), err = command.execute_with_conf_and_rc(r'/usr/bin/pdbedit  -d 1 -t -a  -u %s -f %s'%(username, name), "%s\n%s"%(pswd, pswd))
      if err:
        raise Exception(err)
      if rc != 0:
        #print command.get_error_list(ret)
        #print ret, rc
        err = ''
        tl, er = command.get_output_list(ret)
        if er:
          raise Exception(er)
        if tl:
          err = ','.join(tl)
        tl, er = command.get_error_list(ret)
        if er:
          raise Exception(er)
        if tl:
          err = err + ','.join(tl)
        raise Exception("Error creating user's CIFS access : %s "%err)
      #ul = command.get_output_list(ret)
      #print ul
  except Exception, e:
    return False, 'Error creating local user : %s'%str(e)
  else:
    return True, None

def create_local_group(grpname, gid = None):
  try:
    #First check if groups exists. if so kick out
    gl, err = get_local_groups()
    if gl:
      for gd in gl:
        if gd["grpname"] == grpname:
          raise Exception("Error creating group. The group \"%s\" already exists. "%grpname)
    elif err:
      raise Exception("Error retrieving group list : %s"%err)

    use_salt, err = common.use_salt()
    if err:
      raise Exception(err)
    if use_salt:
      client = salt.client.LocalClient()
      if not gid:
        rc = client.cmd('*', 'group.add', [grpname])
      else:
        rc = client.cmd('*', 'group.add', [grpname,gid])
      print rc
      if not rc:
        raise Exception('Group creation failed')
      for hostname, status in rc.items():
        if not status:
          raise Exception('Group creation failed')
    else:
      if gid:
        cmd_to_run = 'groupadd  -g %s %s'%(gid, grpname)
      else:
        cmd_to_run = 'groupadd   %s'%(grpname)
      (ret, rc), err = command.execute_with_rc(cmd_to_run)
      if err:
        raise Exception(err)
      if rc != 0:
        err = ''
        tl, er = command.get_output_list(ret)
        if er:
          raise Exception(er)
        if tl:
          err = ','.join(tl)
        tl, er = command.get_error_list(ret)
        if er:
          raise Exception(er)
        if tl:
          err = err + ','.join(tl)
        raise Exception("Return code : %d. Error : %s"%(rc, err))
  except Exception, e:
    return False, 'Error creating a local group : %s'%str(e)
  else:
    return True, None

def set_local_user_gid(d):
  try:
    if 'username' not in d:
      raise Exception('Unknown user')
    ud, err = get_local_user(d['username'])
    if err:
      raise Exception('Error looking up user information : %s'%err)
    if not ud:
      raise Exception('Specified user information not found.')
    (ret, rc), err = command.execute_with_conf_and_rc(r'usermod  -g %s %s'%(d['gid'], d['username']))
    if err:
      raise Exception(err)
    if rc != 0:
      err = ''
      out, error = command.get_error_list(ret)
      if error:
        raise Exception(error)
      err += ','.join(out)
      out, error = command.get_output_list(ret)
      if error:
        raise Exception(error)
      err += ','.join(out)
      #print ret, rc
      raise Exception(err)

  except Exception, e:
    return False, 'Error setting local user group : %s'%str(e)
  else:
    return True, None

def set_local_user_group_membership(d):
  try:
    if 'username' not in d:
      raise Exception('Unknown user')
    ud, err = get_local_user(d['username'])
    if err:
      raise Exception('Error looking up user information : %s'%err)
    if not ud:
      raise Exception('Specified user information not found.')
    glist = None
    if 'groups' in d:
      glist = d['groups']
    if not glist:
      glist = []
      glist.append(ud['grpname'])
    
    (ret, rc), err = command.execute_with_conf_and_rc(r'usermod  -G %s %s'%(','.join(glist), d['username']))
    if rc != 0:
      err = ''
      out, error = command.get_error_list(ret)
      if error:
        raise Exception(error)
      err += ','.join(out)
      out, error = command.get_output_list(ret)
      if error:
        raise Exception(error)
      err += ','.join(out)
      #print ret, rc
      raise Exception(err)

  except Exception, e:
    return False, "Error setting local user's additional groups : %s"%str(e)
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

    use_salt, err = common.use_salt()
    if err:
      raise Exception(err)
    if use_salt:
      client = salt.client.LocalClient()
      rc = client.cmd('*', 'user.delete', [username] )
      #print rc
      if rc:
        for hostname, status in rc.items():
          if not status:
            raise Exception("Error deleting the system user")
      else:
            raise Exception("Error deleting the system user")
    else:
      cmd_to_run = 'userdel  %s'%(username)
      (ret, rc), err = command.execute_with_rc(cmd_to_run)
      if err:
        raise Exception(err)
      if rc != 0:
        err = ''
        tl, er = command.get_output_list(ret)
        if er:
          raise Exception(er)
        if tl:
          err = ','.join(tl)
        tl, er = command.get_error_list(ret)
        if er:
          raise Exception(er)
        if tl:
          err = err + ','.join(tl)
        raise Exception("Return code : %d. Error : %s"%(rc, err))

    if d['smb_user']:
      (ret, rc), err = command.execute_with_rc(r'pdbedit -d 1 -x %s'%username)
      if err:
        raise Exception(err)
      if rc != 0:
        err = ''
        tl, er = command.get_output_list(ret)
        if er:
          raise Exception(er)
        if tl:
          err = ','.join(tl)
        tl, er = command.get_error_list(ret)
        if er:
          raise Exception(er)
        if tl:
          err = err + ','.join(tl)
        raise Exception("Error deleting user from the cifs storage system. : %s. "%err)
    
  except Exception, e:
    return False, 'Error deleting local user : %s'%str(e)
  else:
    return True, None

def delete_local_group(grpname):

  try:
    if not grpname:
      raise Exception('No username specified')
    d, err = get_local_group(grpname)
    if not d:
      if err:
        raise Exception('Error locating group : %s'%err)
      else:
        raise Exception('Error locating group')

    use_salt, err = common.use_salt()
    if err:
      raise Exception(err)
    if use_salt:
      client = salt.client.LocalClient()
      rc = client.cmd('*', 'group.delete', [grpname] )
      #print rc
      if rc:
        for hostname, status in rc.items():
          if not status:
            raise Exception("Error deleting the system group")
      else:
            raise Exception("Error deleting the system group")
    else:
      cmd_to_run = 'groupdel  %s'%(grpname)
      (ret, rc), err = command.execute_with_rc(cmd_to_run)
      if err:
        raise Exception(err)
      if rc != 0:
        err = ''
        tl, er = command.get_output_list(ret)
        if er:
          raise Exception(er)
        if tl:
          err = ','.join(tl)
        tl, er = command.get_error_list(ret)
        if er:
          raise Exception(er)
        if tl:
          err = err + ','.join(tl)
        raise Exception("Return code : %d. Error : %s"%(rc, err))
    
  except Exception, e:
    return False, 'Error deleting local group : %s'%str(e)
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
    (ret, rc), err = command.execute_with_conf_and_rc(r'echo \"%s:%s\"|chpasswd'%(username, pswd))
    if err:
      raise Exception(err)
    if rc != 0:
      err = ''
      tl, er = command.get_output_list(ret)
      if er:
        raise Exception(er)
      if tl:
        err = ','.join(tl)
      tl, er = command.get_error_list(ret)
      if er:
        raise Exception(er)
      if tl:
        err = err + ','.join(tl)
      raise Exception("Return code : %d. Error : %s"%(rc, err))
      #print ret
      #print command.get_error_list(ret)

    if 'smb_user' in d and d['smb_user']:
      (ret, rc), err = command.execute_with_conf_and_rc(r'smbpasswd -s %s'%(username), "%s\n%s"%(pswd, pswd))
      if err:
        raise Exception(err)
      if rc != 0:
        #print ret
        #print command.get_error_list(ret)
        #ul = command.get_output_list(ret)
        err = ''
        tl, er = command.get_output_list(ret)
        if er:
          raise Exception(er)
        if tl:
          err = ','.join(tl)
        tl, er = command.get_error_list(ret)
        if er:
          raise Exception(er)
        if tl:
          err = err + ','.join(tl)
        raise Exception("Error changing CIFS password : %s. "%err)
  except Exception, e:
    return False, 'Error changing local user password : %s'%str(e)
  else:
    return True, None


def get_local_group(grp, by_name=True, grp_list = None):
  ret = None
  try:
    if not grp:
      raise Exception('No group id or name specified')
    if not grp_list:
      grp_list, err = get_local_groups()
    if not grp_list :
      if err:
        raise Exception('Error retrieving group list : %s'%err)
      else:
        raise Exception('Specified group not found')
    for gd in grp_list:
      if by_name:
        search_term = gd['grpname']
      else:
        search_term = gd['gid']
      if search_term == grp:
        ret = gd
        break
  except Exception, e:
    return None, 'Error retrieving local group : %s'%str(e)
  else:
    return ret, None

def get_local_groups(get_system_groups = False):
  grp_list = []
  try:
    all = grp.getgrall()
    for g in all:
      if not get_system_groups:
        if g.gr_gid < 501:
          continue
      d = {}
      d['grpname'] = g.gr_name
      d['gid'] = g.gr_gid
      d['members'] = g.gr_mem
      ul,err = get_local_users()
      if err:
        raise Exception(err)
      if ul:
        for u in ul:
          if u['gid'] == d['gid'] and u['username'] not in d['members']:
            d['members'].append(u['username'])
            
      grp_list.append(d)
  except Exception, e:
    None, 'Error retrieving local groups : %s'%str(e)
  else:
    return grp_list, None

def get_local_user(user, by_name=True, user_list = None):
  ret = None
  try:
    if not user:
      raise Exception('No user id or name specified')
    if not user_list:
      user_list, err = get_local_users()
    if not user_list :
      if err:
        raise Exception('Error retrieving user list : %s'%err)
      else:
        raise Exception('Specified user not found')
    for ud in user_list:
      if by_name:
        search_term = ud['username']
      else:
        search_term = ud['uid']
      if search_term == user:
        ret = ud
        break
    if ret:
      gd, err = get_local_group(ret['gid'], False)
      if err:
        raise Exception(err)
      if gd:
        ret['grpname'] = gd['grpname']
  except Exception, e:
    return None, 'Error retrieving local user : %s'%str(e)
  else:
    return ret, None

def get_local_users(get_system_users=False):
  user_list = []
  try:
    sys_ul = []
    smb_ul = []
    all = pwd.getpwall()
    #print all
    for user in all:
      if not get_system_users:
        if user.pw_gid < 501:
          continue
      sys_ul.append(user.pw_name)
      d = {}
      d['uid'] = user.pw_uid
      d['gid'] = user.pw_gid
      d['home_dir'] = user.pw_dir
      d['username'] = user.pw_name
      d['comment'] = user.pw_gecos
      d['shell'] = user.pw_shell
      g = grp.getgrgid(d['gid'])
      if g:
        d['grpname'] = g.gr_name
      groups = [g.gr_name for g in grp.getgrall() if d['username'] in g.gr_mem and g.gr_gid != d['gid']]
      gid = pwd.getpwnam(d['username']).pw_gid
      d['other_groups'] = groups
      user_list.append(d)
    (ret, rc), err = command.execute_with_rc("/usr/bin/pdbedit -d 1 -L")
    if err:
      raise Exception(err)
    if rc != 0:
      err = ''
      tl, er = command.get_output_list(ret)
      if er:
        raise Exception(er)
      if tl:
        err = ','.join(tl)
      tl, er = command.get_error_list(ret)
      if er:
        raise Exception(er)
      if tl:
        err = err + ','.join(tl)
      raise "Error retrieving user list : %s"%err

    ul, err = command.get_output_list(ret)
    if err:
      raise Exception(err)
    if ul:
      smb_ul = []
      smb_dict = {}
      for u in ul:
        l = u.split(':')
        if l:
          if len(l) > 1:
            smb_dict['name'] = l[2]
          smb_ul.append(l[0])
    if user_list:
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
  #print get_local_users()
  #print get_local_groups()
  print get_local_group('ram')
  #print get_local_user('ram')

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
    (ret, rc), err = command.execute_with_rc(r'userdel %s'%userid)
    if err:
      raise Exception(err)
    if rc != 0:
      err = ''
      tl, er = command.get_output_list(ret)
      if er:
        raise Exception(er)
      if tl:
        err = ','.join(tl)
      tl, er = command.get_error_list(ret)
      if er:
        raise Exception(er)
      if tl:
        err = err + ','.join(tl)
      raise Exception("Return code : %d. Error : %s"%(rc, err))
    #print "Deleted user %s from the system"%userid
    client = salt.client.LocalClient()
    rc = client.cmd('*', 'user.delete', [userid] )
    for hostname, status in rc.items():
      if not status:
        error_list.append("Error deleting the userid on GRIDCell %s"%hostname)

  #print "Deleting user %s from the storage system"%userid
  (ret, rc), err = command.execute_with_rc(r'pdbedit -d 1 -x %s'%userid)
  if rc != 0:
    raise Exception("Error deleting user from the storage system. Return code : %d. "%rc)
  #print "Deleted user %s from the storage system"%userid
  return error_list
'''
