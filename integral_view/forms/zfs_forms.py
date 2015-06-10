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

class CreatePoolForm(forms.Form):
  name = forms.CharField()
  
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
      if 'raid10' in pol:
        self.fields['stripe_width'] = forms.IntegerField(required=False)
      self.fields['pool_type'] = forms.ChoiceField(choices=ch)

  def clean(self):
    cd = super(CreatePoolForm, self).clean()
    if cd['pool_type'] == 'raid10':
      if ('stripe_width' not in cd) or (not cd['stripe_width']):
        self._errors["stripe_width"] = self.error_class(["Stripe width is required for a RAID 10 pool"])
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
