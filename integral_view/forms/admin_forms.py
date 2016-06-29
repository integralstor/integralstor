from django import forms

import re
from email.utils import parseaddr

class _MultipleEmailField(forms.CharField):

  def _is_valid_email(self, email):
    try:
      email = email.strip()
      t = parseaddr(email)
      # This is because t[1] is the email address
      if t[1]:
        if not '@' in t[1]:
          return None, 'Error validating email address : %s. Check if your email host is correct'%str(e)
        if not re.match('^[A-Za-z0-9._%+-]+@[A-Za-z0-9\.\-]+', email):
          return None, 'Error validating email address : %s. Wrongly formatted email ?'%str(e)
        return True,None
      else:
        return False,"Not valid email address. Enter a valid email address"
    except Exception, e:
      return None, 'Error validating email address : %s'%str(e)
    else:
      return ret, None

    
  def clean(self, value):
    if not value:
      return forms.ValidationError("Enter atleast one email address")
    if ',' in value:
      emails = value.lower().split(',')
    else:
      emails = value.lower().split(' ')
    for email in emails:
      ret, err = self._is_valid_email(email)
      if err:
        raise forms.ValidationError(err)
      if not ret:
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

  server = forms.CharField(required=True)
  port = forms.IntegerField(required=True)
  username = forms.CharField(required=True)
  pswd = forms.CharField(widget=forms.PasswordInput())
  tls = forms.BooleanField(required=False)
  rcpt_list = _MultipleEmailField(required=True)
  email_alerts = forms.BooleanField(required=False)
  email_audit = forms.BooleanField(required=False)
  email_quota = forms.BooleanField(required=False,widget=forms.HiddenInput())

