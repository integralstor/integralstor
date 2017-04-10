from django import forms


class DateTimeForm(forms.Form):
    system_time = forms.CharField(required=False)
    system_date = forms.CharField(required=False)

    def clean(self):
        cd = super(DateTimeForm, self).clean()
        if ('system_time' not in cd or cd['system_time'] == '') and ('system_date' not in cd or cd['system_date'] == ''):
            raise forms.ValidationError(
                "Atleast date or time should be present")
        else:
            if cd['system_date'] == '':
                cd['system_date'] = None
            if cd['system_time'] == '':
                cd['system_time'] = None
            return cd
