from django import forms
import logging

class SystemLogsForm(forms.Form):
  """ Form to get the info about which system log to download"""

  ch = [('boot','Boot log'), ('dmesg', 'Dmesg log'), ('message', 'Message log'),('smb', 'Samba logs'),('winbind', 'Samba Winbind logs'),('ctdb', 'CTDB logs')]
  sys_log_type = forms.ChoiceField(choices=ch)

  def __init__(self, *args, **kwargs):

    if kwargs:
      si = kwargs.pop('system_config_list')

    super(SystemLogsForm, self).__init__(*args, **kwargs)
    ch = []

    if si:
      for hostname in si.keys():
        if si[hostname]["node_status"] < 0:
          continue
        tup = (hostname,hostname)
        ch.append(tup)
    self.fields['hostname'] = forms.ChoiceField(choices = ch)

class IntegralViewLoggingForm(forms.Form):

  ch = [(logging.DEBUG, 'Debug'), (logging.INFO, 'Information'), (logging.WARNING, 'Errors')]
  log_level = forms.ChoiceField(choices=ch)
