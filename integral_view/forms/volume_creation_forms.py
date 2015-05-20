from django import forms
import fractalio
from fractalio import volume_info

class VolTypeForm(forms.Form):
  ch = [('distributed', r'Distribute my files across disks(Higher performance, no reduncancy)'), ('replicated', r'Make copies of  my files across multiple disks (Redundancy with higher storage overhead)')]
  vol_type = forms.ChoiceField(choices=ch, widget=forms.RadioSelect())
  vol_name = forms.CharField(widget=forms.HiddenInput)
  vol_access = forms.CharField(widget=forms.HiddenInput)

class VolOndiskStorageForm(forms.Form):
  ch = [('compressed', r'Enable compression'), ('deduplicated', r'Enable deduplication'), ('normal', r'None of the above')]
  ondisk_storage = forms.ChoiceField(choices=ch, widget=forms.RadioSelect())
  vol_name = forms.CharField(widget=forms.HiddenInput)
  vol_access = forms.CharField(widget=forms.HiddenInput)
  vol_type = forms.CharField(widget=forms.HiddenInput)

class VolAccessMethodForm(forms.Form):
  ch = [('iscsi', r'ISCSI block device access'), ('file', r'File based access (NFS or CIFS)')]
  vol_access = forms.ChoiceField(choices=ch, widget=forms.RadioSelect())
  vol_name = forms.CharField(widget=forms.HiddenInput)


class VolumeNameForm(forms.Form):
  volume_name = forms.CharField()

  def clean_volume_name(self):
    name = self.cleaned_data["volume_name"]
    if volume_info.volume_exists(None, name):
      raise forms.ValidationError("A volume by this name already exists. Please select another name.")
    return name



'''

class ReplicationCountForm(forms.Form):
  """ Not used for now as we are enforcing a count of 2 but keep for later """
  ch = [('2', r'2 - Will use TWICE the space required by each file'), ('3', r'3 - Will use 3 TIMES the space required by each file')]
  #repl_count = forms.ChoiceField(choices=ch, widget=forms.RadioSelect())
  repl_count = forms.ChoiceField(choices=ch)
  vol_name = forms.CharField(widget=forms.HiddenInput)
  vol_type = forms.CharField(widget=forms.HiddenInput)

  def __init__(self, *args, **kwargs):
    vol_name = None
    vol_type = None
    if kwargs :
      vol_name = kwargs.pop('vol_name')
      vol_type = kwargs.pop('vol_type')
    super(ReplicationCountForm, self).__init__(*args, **kwargs)
    self.fields['vol_type'].initial = vol_type
    self.fields['vol_name'].initial = vol_name

class CreateVolumeForm(forms.Form) :
  """ Form to create a volume"""

  vol_name = forms.CharField(widget=forms.HiddenInput)
  vol_type = forms.CharField(widget=forms.HiddenInput)
  vol_access = forms.CharField(widget=forms.HiddenInput)
'''
