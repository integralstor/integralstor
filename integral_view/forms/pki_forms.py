from django import forms


class CreateSelfSignedCertForm(forms.Form):

  name = forms.CharField()
  key_length = forms.IntegerField(required=False)
  ch = [('1024', 1024), ('2048', 2048)]
  key_length = forms.ChoiceField(choices=ch)
  days = forms.IntegerField()
  country = forms.CharField(max_length=2, min_length=2)
  state = forms.CharField(required=False)
  location = forms.CharField(required=False)
  o = forms.CharField(required=False)
  ou = forms.CharField(required=False)
  cn = forms.CharField(required=False)
  email = forms.EmailField(required=False)

class UploadCertForm(forms.Form):
  name = forms.CharField()
  certificate = forms.CharField(widget=forms.Textarea)
  private_key = forms.CharField(widget=forms.Textarea)
