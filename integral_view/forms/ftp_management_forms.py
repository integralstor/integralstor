from django import forms


class ConfigureFTPForm(forms.Form):

    ssl_enabled = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(
        attrs={'onclick': 'select_field("id_ssl_enabled");'}))

    def __init__(self, *args, **kwargs):
        dsl = None
        cnl = None
        if kwargs:
            if 'datasets' in kwargs:
                dsl = kwargs.pop('datasets')
            if 'cert_names' in kwargs:
                cnl = kwargs.pop('cert_names')
        super(ConfigureFTPForm, self).__init__(*args, **kwargs)

        ch = []
        if dsl:
            for i in dsl:
                tup = (i, i)
                ch.append(tup)
            self.fields['dataset'] = forms.ChoiceField(choices=ch)

        ch = []
        if cnl:
            for i in cnl:
                tup = (i, i)
                ch.append(tup)
            self.fields['cert_name'] = forms.ChoiceField(choices=ch)

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
