from django import forms
import logging

class SystemLogsForm(forms.Form):
  """ Form to get the info about which system log to download"""

  ch = [('boot','Boot log'), ('dmesg', 'Dmesg log'), ('message', 'Message log'),('smb', 'Samba logs'),('winbind', 'Samba Winbind logs')]
  sys_log_type = forms.ChoiceField(choices=ch)
  hostname = forms.CharField(widget=forms.HiddenInput)

class IntegralViewLoggingForm(forms.Form):

  ch = [(logging.DEBUG, 'Debug'), (logging.INFO, 'Information'), (logging.WARNING, 'Errors')]
  log_level = forms.ChoiceField(choices=ch)
