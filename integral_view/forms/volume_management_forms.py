from django import forms

class VolumeOptionsForm(forms.Form):

  vol_name = forms.CharField(widget = forms.HiddenInput)
  auth_allow = forms.CharField(required=False)
  auth_reject = forms.CharField(required=False)
  ch = [('off', 'Read-write'), ('on', 'Read only')]
  readonly = forms.ChoiceField(choices=ch)
  #readonly = forms.ChoiceField(choices=ch, widget=forms.Select(attrs={'onclick': 'set_field_visibility();'}))
  nfs_disable = forms.BooleanField(required=False)
  #nfs_disable = forms.BooleanField(widget=forms.CheckboxInput(attrs={'onclick': 'set_field_visibility();'}), required=False)
  ch = [('read-only', 'Read only'), ('read-write', 'Read-write')]
  nfs_volume_access = forms.ChoiceField(choices=ch, required=False)
  enable_worm = forms.BooleanField(required=False)

  def clean(self):
    cd = super(VolumeOptionsForm, self).clean()
    if "enable_worm" in cd:
      if cd["enable_worm"]:
        if cd["readonly"] == "on":
          self._errors["readonly"] = self.error_class(["You cannot enable Read only and the WORM feature together"])
    return cd

class VolumeQuotaForm(forms.Form):
  vol_name = forms.CharField(widget = forms.HiddenInput)
  set_quota = forms.BooleanField(required=False)
  limit = forms.CharField(required=False)
  ch = [('GB', 'GB'), ('MB', 'MB')]
  unit = forms.ChoiceField(choices=ch, required=False)

  def clean(self):
    cd = super(VolumeQuotaForm, self).clean()
    if "set_quota" in cd :
      if "limit" not in cd:
        self._errors["limit"] = self.error_class(["Please specify a limit"])
        del cd["limit"]
    return cd


class VolumeNameForm(forms.Form):
  """ Form to prompt for the volume name"""

  def __init__(self, *args, **kwargs):
    vl = None
    if kwargs:
      vl = kwargs.pop('vol_list')
    super(VolumeNameForm, self).__init__(*args, **kwargs)
    ch = []
    if vl:
      for i in vl:
        tup = (i,i)
        ch.append(tup)
    self.fields['vol_name'] = forms.ChoiceField(choices=ch)

class CreateSnapshotForm(VolumeNameForm):
  """ Form to prompt for the volume name"""
  
  snapshot_name = forms.CharField()

  def clean_snapshot_name(self):
    snapshot_name = self.cleaned_data['snapshot_name']
    if not snapshot_name[0].isalpha():
      raise forms.ValidationError("The snapshot name should begin with an alphabet")
    if (' ' in snapshot_name):
      raise forms.ValidationError("The snapshot name cannot contain spaces")
    return self.cleaned_data['snapshot_name']

class ReplaceNodeConfForm(forms.Form):

  src_node = forms.CharField()
  dest_node = forms.CharField()

class ReplaceNodeForm(forms.Form):
  """ Form for getting the src and dest nodes for replacing"""

  def __init__(self, *args, **kwargs):
    si = []
    #assert False
    src_node_list = []
    dest_node_list = []
    if kwargs :
      src_node_list = kwargs.pop('src_node_list')
      dest_node_list = kwargs.pop('dest_node_list')
    super(ReplaceNodeForm, self).__init__(*args, **kwargs)
    ch = []
    for hostname in src_node_list:
      tup = (hostname, hostname)
      ch.append(tup)   
    self.fields["src_node"] = forms.ChoiceField(widget=forms.RadioSelect(), choices=ch)

    for hostname in dest_node_list:
      tup = (hostname, hostname)
      ch.append(tup)   
    self.fields["dest_node"] = forms.ChoiceField(widget=forms.RadioSelect(), choices=ch)

  def clean(self):
    cleaned_data = super(ReplaceNodeForm, self).clean()
    dest_node = cleaned_data.get('dest_node')
    src_node = cleaned_data.get('src_node')
    if src_node == dest_node:
      raise forms.ValidationError("Source and replacement GRIDCells should be different")
    return cleaned_data


'''

class ExpandVolumeForm(forms.Form):
  """ Form to prompt for the info to expand a volume"""

  vol_name = forms.CharField(widget=forms.HiddenInput)
  vol_type = forms.CharField(widget=forms.HiddenInput)
  count = forms.IntegerField(widget=forms.HiddenInput, required=False)

  def __init__(self, *args, **kwargs):
    if kwargs:
      scl = kwargs.pop('system_config_list')
      vil = kwargs.pop('volume_info_list')
      vol_name = kwargs.pop('vol_name')
    super(ExpandVolumeForm, self).__init__(*args, **kwargs)
    ch = []
    for vol in vil:
      if vol["name"] == vol_name:
        break
    for node in scl:
      #print "appending!"
      if node["active"] and node["in_cluster"] and "hostname" in node:
        in_vol = False
        for brick in vol["bricks"]:
          if brick["host"] == node["hostname"]:
            in_vol = True
            break
        if not in_vol:
          tup = (node["hostname"], node["hostname"])
          ch.append(tup)   
    self.fields["hosts"] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=ch)

  def clean_hosts(self):
    hosts = self.cleaned_data['hosts']
    count = self.cleaned_data['count']
    if count != 0:
      if len(hosts)%count != 0:
        raise forms.ValidationError("Please choose the a multiple of %d disks"%count)
    return self.cleaned_data['hosts']
'''
