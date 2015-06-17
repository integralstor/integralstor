from django import forms
import integralstor_common

class DatasetForm(forms.Form):

  name = forms.CharField()
  readonly = forms.BooleanField(required=False)
  compression = forms.BooleanField(required=False)
  dedup = forms.BooleanField(required=False)

class CreateDatasetForm(forms.Form):
  name = forms.CharField()
  readonly = forms.BooleanField(required=False)
  compression = forms.BooleanField(required=False)
  dedup = forms.BooleanField(required=False)
  pool = forms.CharField()
  
  def __init__(self, *args, **kwargs):
    dsll = None
    if kwargs:
      dsl = kwargs.pop('datasets')
    super(CreateDatasetForm, self).__init__(*args, **kwargs)
    ch = []
    if dsl:
      for i in dsl:
        tup = (i,i)
        ch.append(tup)
    self.fields['parent'] = forms.ChoiceField(choices=ch)

class SlogForm(forms.Form):
  ch = [('ramdisk', 'RAM disk')]
  slog = forms.ChoiceField(choices=ch)
  ramdisk_size = forms.IntegerField()
  pool = forms.CharField(widget=forms.HiddenInput)

class CreatePoolForm(forms.Form):
  name = forms.CharField()
  num_disks = forms.IntegerField(widget=forms.HiddenInput, required=False)
  
  def __init__(self, *args, **kwargs):
    pol = None
    if kwargs:
      pol = kwargs.pop('pool_types')
    super(CreatePoolForm, self).__init__(*args, **kwargs)
    ch = []
    if pol:
      for i in pol:
        tup = (i,i)
        ch.append(tup)
      if 'raid5' in pol:
        self.fields['num_raid_disks'] = forms.IntegerField(required=False)
      if 'raid10' in pol:
        self.fields['stripe_width'] = forms.IntegerField(required=False)
      self.fields['pool_type'] = forms.ChoiceField(choices=ch)

  def clean(self):
    cd = super(CreatePoolForm, self).clean()
    num_disks = cd['num_disks']
    if cd['pool_type'] in ['raid10', 'raid5', 'raid6']:
      if ('num_raid_disks' not in cd) or (not cd['num_raid_disks']):
        self._errors["num_raid_disks"] = self.error_class(["The number of RAID disks is required for a RAID pool"])
      if cd['num_raid_disks'] > num_disks:
        self._errors["num_raid_disks"] = self.error_class(["The number of RAID disks exceeds the available number of disks. Only %d disks available"%num_disks])
      if cd['pool_type'] == 'raid10':
        if ('stripe_width' not in cd) or (not cd['stripe_width']):
          self._errors["stripe_width"] = self.error_class(["Stripe width is required for a RAID 10 pool"])
        if cd['stripe_width']*cd['num_raid_disks'] > num_disks:
          self._errors["stripe_width"] = self.error_class(["The number of disks with the stripe width and RAID disks combination exceeds the number of available disks. Only %d disks available"%num_disks])
          self._errors["num_raid_disks"] = self.error_class(["The number of RAID disks is required for a RAID pool"])
    return cd


class CreateSnapshotForm(forms.Form):
  name = forms.CharField()
  
  def __init__(self, *args, **kwargs):
    vl = None
    if kwargs:
      dsl = kwargs.pop('datasets')
    super(CreateSnapshotForm, self).__init__(*args, **kwargs)
    ch = []
    if dsl:
      for i in dsl:
        tup = (i,i)
        ch.append(tup)
    self.fields['target'] = forms.ChoiceField(choices=ch)

class RenameSnapshotForm(forms.Form):
  ds_name = forms.CharField(widget=forms.HiddenInput)
  snapshot_name = forms.CharField(widget=forms.HiddenInput)
  new_snapshot_name = forms.CharField()
