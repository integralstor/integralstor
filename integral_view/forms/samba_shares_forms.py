from django import forms
import integralstor_common
from integralstor_common import networking
from integral_view.forms import folder_management_forms

class AuthADSettingsForm(forms.Form):
  security = forms.CharField(widget=forms.HiddenInput)
  password = forms.CharField(widget=forms.PasswordInput())
  realm = forms.CharField()
  workgroup = forms.CharField()
  password_server = forms.CharField()
  password_server_ip = forms.CharField()
  netbios_name = forms.CharField()

  def clean(self):
    cd = super(AuthADSettingsForm, self).clean()
    if not networking.validate_ip(cd['password_server_ip']):
      del cd["password_server_ip"]
      self._errors["password_server_ip"] = self.error_class(["Please specify a valid IP address"])
    return cd

class AuthUsersSettingsForm(forms.Form):
  security = forms.CharField(widget=forms.HiddenInput)
  workgroup = forms.CharField()
  netbios_name = forms.CharField()


class CreateShareForm(folder_management_forms.DirForm):
  share_id =  forms.IntegerField(widget=forms.HiddenInput, required = False)
  name = forms.CharField()
  comment = forms.CharField(required=False)
  browseable = forms.BooleanField(required=False,initial=True)
  read_only = forms.BooleanField(required=False)
  new_folder = forms.CharField(required=False)

  def __init__(self, *args, **kwargs):
    if kwargs:
      dataset_list = kwargs.pop("dataset_list")
    super(CreateShareForm, self).__init__(*args, **kwargs)

    ch = []
    if dataset_list:
      for ds in dataset_list:
        tup = (ds[0], ds[1])
        ch.append(tup)   
    self.fields['dataset'] =  forms.ChoiceField(widget=forms.Select, choices=ch)


class AddShareAcesForm(folder_management_forms.AddAcesForm):
  share_index =  forms.IntegerField(widget=forms.HiddenInput)
  share_name =  forms.CharField(widget=forms.HiddenInput)

  def __init__(self, *args, **kwargs):
    super(AddShareAcesForm, self).__init__(*args, **kwargs)


class EditShareAcesForm(folder_management_forms.EditAcesForm):
  share_index =  forms.IntegerField(widget=forms.HiddenInput)
  share_name =  forms.CharField(widget=forms.HiddenInput)
  def __init__(self, *args, **kwargs):
    super(EditShareAcesForm, self).__init__(*args, **kwargs)

class EditShareForm(forms.Form):
  share_id =  forms.IntegerField(widget=forms.HiddenInput)
  name = forms.CharField()
  path = forms.CharField(required=False)
  comment = forms.CharField(required=False)
  browseable = forms.BooleanField(required=False)
  read_only = forms.BooleanField(required=False)
  #guest_ok = forms.BooleanField(required=False)

  '''
  def __init__(self, *args, **kwargs):
    if kwargs:
      user_list = kwargs.pop("user_list")
      group_list = kwargs.pop("group_list")
    super(EditShareForm, self).__init__(*args, **kwargs)
    ch = []
    if user_list:
      for user in user_list:
        tup = (user, user)
        ch.append(tup)   
    self.fields["users"] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'onclick':'select_guest_ok();'}), choices=ch,required=False )

    ch = []
    if group_list:
      for gr in group_list:
        tup = (gr, gr)
        ch.append(tup)   
    self.fields["groups"] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'onclick':'select_guest_ok();'}), choices=ch,required=False )

  def clean(self):
    cd = super(EditShareForm, self).clean()
    go = cd['guest_ok']
    us = cd['users']
    gr = cd['users']
    if go:
      if us:
        self._errors["users"] = self.error_class(["This field cannot be set when guest ok is selected"])
        del cd["users"]
      if gr:
        self._errors["groups"] = self.error_class(["This field cannot be set when guest ok is selected"])
        del cd["groups"]
    else:
      if (not us) and (not gr):
        self._errors["guest_ok"] = self.error_class(["This field cannot be left unselected if no users or groups are selected"])
    return cd
  '''

