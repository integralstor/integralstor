from django import forms


class LocalUserForm(forms.Form):

    username = forms.CharField()
    name = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput())
    password_conf = forms.CharField(widget=forms.PasswordInput())

    '''
  def __init__(self, *args, **kwargs):
    if kwargs:
      group_list = kwargs.pop("group_list")
    super(LocalUserForm, self).__init__(*args, **kwargs)

    ch = []
    if group_list:
      for group in group_list:
        tup = (group['gid'], group['grpname'])
        ch.append(tup)   
    self.fields['gid'] =  forms.ChoiceField(widget=forms.Select, choices=ch, required=False)
  '''

    def clean(self):
        cd = super(LocalUserForm, self).clean()
        if "password" in cd and "password_conf" in cd:
            if cd["password"] != cd["password_conf"]:
                self._errors["password"] = self.error_class(
                    ["The password and password confirmation do not match."])
                del cd["password"]
                del cd["password_conf"]

        if "'" in cd["name"] or '"' in cd["name"]:
            self._errors["name"] = self.error_class(
                ["The name cannot contain special characters."])
            del cd["name"]
        if "name" in cd:
            n = cd["name"]
            cd["name"] = "_".join(n.split())
        return cd


class LocalGroupForm(forms.Form):
    grpname = forms.CharField()


class EditLocalUserGidForm(forms.Form):
    username = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        if kwargs:
            group_list = kwargs.pop("group_list")
        super(EditLocalUserGidForm, self).__init__(*args, **kwargs)

        ch = []
        if group_list:
            for group in group_list:
                tup = (group['gid'], group['grpname'])
                ch.append(tup)
        self.fields['gid'] = forms.ChoiceField(widget=forms.Select, choices=ch)


class EditLocalUserGroupMembershipForm(forms.Form):
    username = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        if kwargs:
            group_list = kwargs.pop("group_list")
        super(EditLocalUserGroupMembershipForm, self).__init__(*args, **kwargs)

        ch = []
        if group_list:
            for group in group_list:
                tup = (group['grpname'], group['grpname'])
                ch.append(tup)
        self.fields["groups"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple(), choices=ch, required=False)


class ModifyGroupMembershipForm(forms.Form):
    grpname = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        if kwargs:
            user_list = kwargs.pop("user_list")
        super(ModifyGroupMembershipForm, self).__init__(*args, **kwargs)

        ch = []
        if user_list:
            for user in user_list:
                tup = (user['username'], user['username'])
                ch.append(tup)
        self.fields["users"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple(), choices=ch, required=False)


class PasswordChangeForm(forms.Form):

    username = forms.CharField(widget=forms.HiddenInput)
    password = forms.CharField(widget=forms.PasswordInput())
    password_conf = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cd = super(PasswordChangeForm, self).clean()
        if "password" in cd and "password_conf" in cd:
            if cd["password"] != cd["password_conf"]:
                self._errors["password"] = self.error_class(
                    ["The password and password confirmation do not match."])
                del cd["password"]
                del cd["password_conf"]
        return cd

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
