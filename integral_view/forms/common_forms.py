
from django import forms

from integralstor import networking
from email.utils import parseaddr

class MultipleEmailField(forms.CharField):

    def _is_valid_email(self, email):
        try:
            email = email.strip()
            t = parseaddr(email)
            if t[0] or t[1]:
                if not '@' in t[1]:
                    raise Exception('Invalid email address.')
                if not re.match('^[A-Za-z0-9._%+-]+@[A-Za-z0-9\.\-]+', email):
                    raise Exception('Invalid email address.')
            else:
                raise Exception('Invalid email address.')
        except Exception, e:
            return False, 'Error validating email address : %s' % str(e)
        else:
            return True, None

    def clean(self, value):
        if not value:
            raise forms.ValidationError("Enter atleast one email address")
        if ',' in value:
            emails = value.lower().split(',')
        else:
            emails = value.lower().split(' ')
        for email in emails:
            ret, err = self._is_valid_email(email)
            if err:
                raise forms.ValidationError(err)
            if not ret:
                raise forms.ValidationError(
                    "%s is not a valid email address" % email)

        return value.lower()

class MultipleServerField(forms.CharField):

    def _is_valid_server(self, server):
        server = server.strip()
        ok, err = networking.validate_ip_or_hostname(server)
        if err:
            raise Exception('Error validating server : %s' % err)
        return ok

    def clean(self, value):
        super(MultipleServerField, self).validate(value)
        '''
        if not value:
            raise forms.ValidationError(
                "Enter atleast one IP address or hostname")
        '''
        if not value:
            return None
        if ',' in value:
            servers = value.lower().split(',')
        else:
            servers = value.lower().split(' ')
        for server in servers:
            if not self._is_valid_server(server):
                raise forms.ValidationError(
                    "%s is not a valid address" % server)

        return value.lower()




class FileUploadForm(forms.Form):
    file_field = forms.FileField()

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
