from django import forms
import integralstor_common
from integralstor_common import networking

'''
class AddClientForm(forms.Form):

  ip = forms.CharField()
  ch = [('off', 'Read-write'), ('on', 'Read only')]
  readonly = forms.ChoiceField(choices=ch)
  ch = [('sync', 'Synchronous'), ('async', 'Asynchronous')]
  sync = forms.ChoiceField(choices=ch)
  root_squash = forms.BooleanField(required=False)
  all_squash = forms.BooleanField(required=False)
'''

class ShareForm(forms.Form):

  path = forms.CharField()
  clients = forms.CharField()
  readonly = forms.BooleanField(required=False)
  root_squash = forms.BooleanField(required=False)
  all_squash = forms.BooleanField(required=False)

class CreateShareForm(ShareForm):

  dataset = forms.CharField(required=True)

  def __init__(self, *args, **kwargs):
    if kwargs:
      dataset_list = kwargs.pop("dataset_list")
    super(CreateShareForm, self).__init__(*args, **kwargs)

    ch = []
    if dataset_list:
      for ds in dataset_list:
        tup = ( ds['mountpoint'], ds['name'])
        ch.append(tup)   
    self.fields["dataset"] = forms.ChoiceField(choices=ch)

