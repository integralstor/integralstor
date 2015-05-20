from django import forms

import fractalio
import fractalio.networking
import common_forms

class InitiatorForm(forms.Form):

  initiators = common_forms.MultipleServerField()
  auth_network = forms.CharField()
  comment = forms.CharField(required=False)

  def clean(self):
    cd = super(InitiatorForm, self).clean()
    if "auth_network" not in cd:
      return cd
    auth_network = cd["auth_network"]
    if cd["initiators"].lower() == 'all':
      cd["initiators"] = 'ALL'
    if cd["auth_network"].lower() == 'all':
      cd["auth_network"] = 'ALL'
    else :
      slash_index = auth_network.find('/')
      if slash_index == -1:
        self._errors["auth_network"] = self.error_class(["Please specify a CIDR network mask"])
      try:
        network_mask = int(auth_network[slash_index+1:])
      except Exception, e: 
        del cd["auth_network"]
        self._errors["auth_network"] = self.error_class(["Please specify a valid CIDR network mask"])
        network_mask = None
      if network_mask:
        if network_mask < 1 or network_mask > 31:
          del cd["auth_network"]
          self._errors["auth_network"] = self.error_class(["CIDR network mask should be between 1 and 31"])
      ip_addr = auth_network[:slash_index]
      if not networking.is_valid_ip(ip_addr):
        del cd["auth_network"]
        self._errors["auth_network"] = self.error_class(["Please specify a valid IP address"])
    return cd

class TargetForm(forms.Form):

  target_name = forms.CharField()
  lun_size = forms.IntegerField()
  vol_name = forms.CharField()
  target_alias = forms.CharField()
  '''
  ch = [('read-write', 'Read Write'), ('read-only', 'Read Only')]
  target_flags =  forms.ChoiceField(widget=forms.Select, choices=ch)
  '''
  ch = [('CHAP', 'CHAP'), ('None', 'None')]
  auth_method =  forms.ChoiceField(widget=forms.Select, choices=ch)
  queue_depth = forms.IntegerField(min_value=0, max_value=255, initial=32)

  def __init__(self, *args, **kwargs):
    aal = []
    igl = []
    if kwargs:
      aal = kwargs.pop("auth_access_group_list")
      igl = kwargs.pop("initiator_group_list")
      vl = kwargs.pop("volumes_list")
    super(TargetForm, self).__init__(*args, **kwargs)
    ch = []
    for v in vl:
      tup = (v,v)
      ch.append(tup)
    self.fields["vol_name"] =  forms.ChoiceField(widget=forms.Select, choices=ch)
    ch = []
    for a in aal:
      tup = (a["id"],a["id"])
      ch.append(tup)
    self.fields["auth_group_id"] =  forms.ChoiceField(widget=forms.Select, choices=ch)
    ch = []
    for i in igl:
      tup = (i["id"],i["id"])
      ch.append(tup)
    self.fields["init_group_id"] =  forms.ChoiceField(widget=forms.Select, choices=ch)


class AuthorizedAccessUserForm(forms.Form):

  user = forms.CharField()
  auth_access_group_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
  user_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
  secret = forms.CharField(widget=forms.PasswordInput())
  secret_conf = forms.CharField(widget=forms.PasswordInput())
  #peer_user = forms.CharField(required=False)
  #peer_secret = forms.CharField(widget=forms.PasswordInput(), required=False)
  #peer_secret_conf = forms.CharField(widget=forms.PasswordInput(), required=False)

  def clean(self):
    cd = super(AuthorizedAccessUserForm, self).clean()
    if cd["secret"] != cd["secret_conf"]:
      self._errors["secret_conf"] = self.error_class(["Secret and confirmation do not match"])
      del cd["secret_conf"]
    '''
    elif "peer_user" in cd:
      if cd["peer_user"] :
        if not cd["peer_secret"]:
          self._errors["peer_secret"] = self.error_class(["Peer secret is required if peer user is specified"])
          del cd["peer_secret"]
        else:
          if cd["peer_secret"] != cd["peer_secret_conf"]:
            self._errors["peer_secret_conf"] = self.error_class(["Peer secret and confirmation do not match"])
            del cd["peer_secret_conf"]
          if "secret" in cd and "peer_secret" in cd:
            if cd["peer_secret"] == cd["secret"]:
              self._errors["peer_secret"] = self.error_class(["Peer secret cannot be the same as the secret "])
              del cd["peer_secret"]
              if "peer_secret_conf" in cd:
                del cd["peer_secret_conf"]
    '''
    self.data = cd
    return cd

class TargetGlobalConfigForm(forms.Form):
  ch = [('CHAP', 'CHAP'), ('None', 'None')]
  base_name = forms.CharField(initial="iqn.2014-15.org.fractalio:test")
  discovery_auth_method =  forms.ChoiceField(widget=forms.Select, choices=ch)
  io_timeout = forms.IntegerField(min_value=0, max_value=300, initial=30)
  nop_in_interval = forms.IntegerField(min_value=0, max_value=300, initial=20)
  max_sessions = forms.IntegerField(min_value=1, max_value=65536, initial=16)
  max_connections = forms.IntegerField(min_value=1, max_value=65536, initial=8)
  max_presend_r2t = forms.IntegerField(min_value=1, max_value=255, initial=32)
  max_outstanding_r2t = forms.IntegerField(min_value=1, max_value=255, initial=16)
  first_burst_length = forms.IntegerField(min_value=1, max_value=4294967296, initial=65536)
  max_burst_length = forms.IntegerField(min_value=1, max_value=4294967296, initial=262144)
  max_receive_data_segment_length = forms.IntegerField(min_value=1, max_value=4294967296, initial=262144)
  default_time_to_wait = forms.IntegerField(min_value=1, max_value=300, initial=2)
  default_time_to_retain = forms.IntegerField(min_value=1, max_value=300, initial=60)
  '''
  enable_luc = forms.BooleanField()
  controller_ip_addr = forms.GenericIPAddressField(protocol='ipv4', required=False)
  controller_tcp_port = forms.IntegerField(min_value=1024, max_value=65535, initial=3261, required=False)
  controller_auth_netmask = forms.GenericIPAddressField(protocol='ipv4', required=False)
  ch = [('CHAP', 'CHAP'), ('MCHAP','Mutual CHAP'), ('None', 'None'), ('Auto','Auto')]
  controller_auth_method =  forms.ChoiceField(widget=forms.Select, choices=ch)
  '''
  '''
  def clean(self):
    cd = super(TargetGlobalConfigForm, self).clean()
    if "enable_luc" in cd and cd["enable_luc"]:
      if "controller_ip_addr" not in cd:
        self._errors["controller_ip_addr"] = self.error_class(["This field is required if LUC is enabled"])
        del cd["controller_ip_addr"]
      if "controller_tcp_port" not in cd:
        self._errors["controller_tcp_port"] = self.error_class(["This field is required if LUC is enabled"])
        del cd["controller_tcp_port"]
      if "controller_auth_netmask" not in cd:
        self._errors["controller_auth_netmask"] = self.error_class(["This field is required if LUC is enabled"])
        del cd["controller_auth_netmask"]
    return cd
  '''

  def __init__(self, *args, **kwargs):
    aal = []
    if kwargs:
      aal = kwargs.pop("auth_access_group_list")
    super(TargetGlobalConfigForm, self).__init__(*args, **kwargs)
    ch = []
    for a in aal:
      tup = (a["id"],a["id"])
      ch.append(tup)
    #self.fields["controller_auth_group"] =  forms.ChoiceField(widget=forms.Select, choices=ch)
    self.fields["discovery_auth_group"] =  forms.ChoiceField(widget=forms.Select, choices=ch)


