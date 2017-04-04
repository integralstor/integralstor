from django import forms


class date_time_form(forms.Form):
    time = forms.CharField()
    date = forms.CharField()
