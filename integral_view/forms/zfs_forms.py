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
    vl = None
    if kwargs:
      dsl = kwargs.pop('datasets')
    super(CreateDatasetForm, self).__init__(*args, **kwargs)
    ch = []
    if dsl:
      for i in dsl:
        tup = (i,i)
        ch.append(tup)
    self.fields['parent'] = forms.ChoiceField(choices=ch)


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
