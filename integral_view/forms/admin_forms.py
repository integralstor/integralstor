from django import forms

import re
from email.utils import parseaddr

class _MultipleEmailField(forms.CharField):

  def _is_valid_email(self, email):
    email = email.strip()
    t = parseaddr(email)
    if t[0] or t[1]:
      if not '@' in t[1]:
        return False
      if not re.match('^[A-Za-z0-9._%+-]+@[A-Za-z0-9\.\-]+', email):
        return False
      return True
    else:
      return False
    
  def clean(self, value):
    if not value:
      return forms.ValidationError("Enter atleast one email address")
    if ',' in value:
      emails = value.lower().split(',')
    else:
      emails = value.lower().split(' ')
    for email in emails:
      if not self._is_valid_email(email):
        raise forms.ValidationError("%s is not a valid email address"%email)

    return value.lower()


class LoginForm(forms.Form):
  """ Form for the login prompt"""
  username = forms.CharField()
  password = forms.CharField(widget=forms.PasswordInput())

class ChangeAdminPasswordForm(forms.Form):
  """ Form for the change admin password prompt"""

  oldPasswd = forms.CharField(widget=forms.PasswordInput())
  newPasswd1 = forms.CharField(min_length=6, widget=forms.PasswordInput())
  newPasswd2 = forms.CharField(min_length=6, widget=forms.PasswordInput())

class ConfigureEmailForm(forms.Form):

  email_server = forms.CharField()
  email_server_port = forms.IntegerField()
  username = forms.CharField()
  pswd = forms.CharField(widget=forms.PasswordInput())
  tls = forms.BooleanField(required=False)
  rcpt_list = _MultipleEmailField()

  email_alerts = forms.BooleanField(required=False)


