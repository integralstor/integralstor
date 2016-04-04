from django import forms

class CreateSelfSignedCertForm(forms.Form):

  name = forms.CharField()
  country = forms.CharField(max_length=2, min_length=2)
  state = forms.CharField(required=False)
  location = forms.CharField(required=False)
  o = forms.CharField(required=False)
  ou = forms.CharField(required=False)
  cn = forms.CharField(required=False)
  key_length = forms.IntegerField(required=False)
  days = forms.IntegerField()
  email = forms.EmailField(required=False)

  ch = [('1024', 1024), ('2048', 2048)]
  key_length = forms.ChoiceField(choices=ch)

class UploadCertForm(forms.Form):
  name = forms.CharField()
  certificate = forms.CharField(widget=forms.Textarea)
  private_key = forms.CharField(widget=forms.Textarea)

class SetHttpsModeForm(forms.Form):
  def __init__(self, *args, **kwargs):
    cert_list = None
    if kwargs and 'cert_list' in kwargs:
      cert_list = kwargs.pop('cert_list')
    super(SetHttpsModeForm, self).__init__(*args, **kwargs)
    if cert_list:
      ch = []
      for cert in cert_list:
        ch.append((cert['name'], cert['name']))
      self.fields['cert_name'] = forms.ChoiceField(choices=ch)
