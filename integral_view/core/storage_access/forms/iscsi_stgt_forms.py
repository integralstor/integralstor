
from django import forms


class IscsiAuthenticationForm(forms.Form):

    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    password_conf = forms.CharField(widget=forms.PasswordInput())
    authentication_type = forms.CharField(widget=forms.HiddenInput)
    target_name = forms.CharField(widget=forms.HiddenInput)


class IscsiTargetForm(forms.Form):

    name = forms.CharField()


class IscsiLunForm(forms.Form):

    target_name = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        if kwargs:
            zvols = kwargs.pop('zvols')
        super(IscsiLunForm, self).__init__(*args, **kwargs)

        ch = []
        if zvols:
            for zvol in zvols:
                tup = (zvol['path'], zvol['name'])
                ch.append(tup)
        self.fields['path'] = forms.ChoiceField(choices=ch)


class IscsiAclForm(forms.Form):

    target_name = forms.CharField(widget=forms.HiddenInput)
    acl = forms.CharField()

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
