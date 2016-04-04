from django import forms

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

