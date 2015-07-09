
from django import forms

import re

import integralstor_common
import integralstor_common.networking

class SetFileOwnerAndPermissionsForm(forms.Form):

  owner_read = forms.BooleanField(required=False)
  owner_write = forms.BooleanField(required=False)
  owner_execute = forms.BooleanField(required=False)
  group_read = forms.BooleanField(required=False)
  group_write = forms.BooleanField(required=False)
  group_execute = forms.BooleanField(required=False)
  other_read = forms.BooleanField(required=False)
  other_write = forms.BooleanField(required=False)
  other_execute = forms.BooleanField(required=False)

  path = forms.CharField(widget=forms.HiddenInput)

  set_owner = forms.BooleanField(required=False)
  set_group = forms.BooleanField(required=False)

  def __init__(self, *args, **kwargs):
    if kwargs:
      group_list = kwargs.pop("group_list")
      user_list = kwargs.pop("user_list")
    super(SetFileOwnerAndPermissionsForm, self).__init__(*args, **kwargs)
    ch = []
    if group_list:
      for group in group_list:
        tup = (group['gid'], group['grpname'])
        ch.append(tup)   
    self.fields['gid'] =  forms.ChoiceField(widget=forms.Select, choices=ch, required=False)
    if user_list:
      for user in user_list:
        tup = (user['uid'], user['username'])
        ch.append(tup)   
    self.fields['uid'] =  forms.ChoiceField(widget=forms.Select, choices=ch, required=False)

class MultipleServerField(forms.CharField):

  def _is_valid_server(self, server):
    server = server.strip()
    if fractalio.networking.is_valid_ip_or_hostname(server):
      return True
    else:
      return False
    
  def clean(self, value):
    if not value:
      raise forms.ValidationError("Enter atleast one IP address or hostname")
    if ',' in value:
      servers = value.lower().split(',')
    else:
      servers = value.lower().split(' ')
    for server in servers:
      if not self._is_valid_server(server):
        raise forms.ValidationError("%s is not a valid address"%server)

    return value.lower()

class ConfigureNTPForm(forms.Form):

  server_list = MultipleServerField()

class AddNodesForm(forms.Form):
  def __init__(self, *args, **kwargs):
    if kwargs:
      pml = kwargs.pop('pending_minions_list')
    super(AddNodesForm, self).__init__(*args, **kwargs)
    ch = []
    for minion in pml:
      tup = (minion, minion)
      ch.append(tup)   
    self.fields["nodes"] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=ch)
