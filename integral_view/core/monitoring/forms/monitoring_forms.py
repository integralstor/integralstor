from django import forms

class RemoteMonitoringServerForm(forms.Form):

    ip = forms.GenericIPAddressField(protocol='IPv4')
    name = forms.CharField()

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
