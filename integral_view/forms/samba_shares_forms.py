from django import forms
import fractalio
from fractalio import networking

class AuthADSettingsForm(forms.Form):
  security = forms.CharField(widget=forms.HiddenInput)
  password = forms.CharField(widget=forms.PasswordInput())
  #ch = [ ('rfc2307', 'Identity Management For Unix'), ('sfu', 'Services For Unix')]
  #ad_schema_mode =  forms.ChoiceField(widget=forms.Select, choices=ch)
  #id_map_min = forms.IntegerField()
  #id_map_max = forms.IntegerField()
  realm = forms.CharField()
  workgroup = forms.CharField()
  password_server = forms.CharField()
  password_server_ip = forms.CharField()
  netbios_name = forms.CharField()

  def clean(self):
    cd = super(AuthADSettingsForm, self).clean()
    if not networking.is_valid_ip(cd['password_server_ip']):
      del cd["password_server_ip"]
      self._errors["password_server_ip"] = self.error_class(["Please specify a valid IP address"])
    return cd

  '''
  id_map_min.initial = 10000
  id_map_max.initial = 20000

  def clean(self):
    cd = super(AuthADSettingsForm, self).clean()
    if "id_map_min" in cd and "id_map_max" in cd:
      min = cd["id_map_min"]
      max = cd["id_map_max"]
      if min >= max:
        self._errors["id_map_min"] = self.error_class(["The first part of range should be less than the second"])
        del cd["id_map_min"]
        del cd["id_map_max"]
    return cd
  '''

class AuthUsersSettingsForm(forms.Form):
  security = forms.CharField(widget=forms.HiddenInput)
  workgroup = forms.CharField()
  netbios_name = forms.CharField()

class LocalUserForm(forms.Form):

  userid = forms.CharField()
  name = forms.CharField(required=False)
  password = forms.CharField(widget=forms.PasswordInput())
  password_conf = forms.CharField(widget=forms.PasswordInput())

  def clean(self):
    cd = super(LocalUserForm, self).clean()
    if "password" in cd and "password_conf" in cd:
      if cd["password"] != cd["password_conf"]:
        self._errors["password"] = self.error_class(["The password and password confirmation do not match."])
        del cd["password"]
        del cd["password_conf"]
    if "'" in cd["name"] or '"' in cd["name"]:
      self._errors["name"] = self.error_class(["The name cannot contain special characters."])
      del cd["name"]
    if "name" in cd:
      n = cd["name"]
      cd["name"] = "_".join(n.split())
    return cd

class PasswordChangeForm(forms.Form):

  userid = forms.CharField(widget=forms.HiddenInput)
  password = forms.CharField(widget=forms.PasswordInput())
  password_conf = forms.CharField(widget=forms.PasswordInput())

  def clean(self):
    cd = super(PasswordChangeForm, self).clean()
    if "password" in cd and "password_conf" in cd:
      if cd["password"] != cd["password_conf"]:
        self._errors["password"] = self.error_class(["The password and password confirmation do not match."])
        del cd["password"]
        del cd["password_conf"]
    return cd

class ShareForm(forms.Form):
  share_id =  forms.IntegerField(widget=forms.HiddenInput, required = False)
  name = forms.CharField()
  path = forms.CharField(required=False)
  display_path = forms.CharField(required=False)
  comment = forms.CharField(required=False)
  browseable = forms.BooleanField(required=False)
  read_only = forms.BooleanField(required=False)
  guest_ok = forms.BooleanField(required=False)

  def __init__(self, *args, **kwargs):
    if kwargs:
      user_list = kwargs.pop("user_list")
      group_list = kwargs.pop("group_list")
      vol_list = kwargs.pop("volume_list")
    super(ShareForm, self).__init__(*args, **kwargs)
    ch = []
    for vol in vol_list:
      tup = (vol["name"], vol["name"])
      ch.append(tup)
    self.fields["vol"] = forms.ChoiceField(choices=ch)
    ch = []
    if user_list:
      for user in user_list:
        tup = (user, user)
        ch.append(tup)   
    self.fields["users"] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'onclick':'select_guest_ok();'}), choices=ch,required=False )
    ch = []
    if group_list:
      for gr in group_list:
        tup = (gr, gr)
        ch.append(tup)   
    self.fields["groups"] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'onclick':'select_guest_ok();'}), choices=ch,required=False )

  def clean(self):
    cd = super(ShareForm, self).clean()
    return cd

