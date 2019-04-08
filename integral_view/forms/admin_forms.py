from django import forms

import re

class LoginForm(forms.Form):
    """ Form for the login prompt"""
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())


class ChangeAdminPasswordForm(forms.Form):
    """ Form for the change admin password prompt"""

    oldPasswd = forms.CharField(widget=forms.PasswordInput())
    newPasswd1 = forms.CharField(min_length=6, widget=forms.PasswordInput())
    newPasswd2 = forms.CharField(min_length=6, widget=forms.PasswordInput())




# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
