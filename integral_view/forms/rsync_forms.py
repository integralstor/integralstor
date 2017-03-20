from django import forms

class ShareForm(forms.Form):
    name = forms.CharField()
    path = forms.CharField()
    comment = forms.CharField(required=False)
    readonly = forms.BooleanField(required=False)
    browsable = forms.BooleanField(required=False)

class CreateShareForm(ShareForm):

    dataset = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        if kwargs:
            dataset_list = kwargs.pop("dataset_list")
        super(CreateShareForm, self).__init__(*args, **kwargs)

        ch = []
        if dataset_list:
            for ds in dataset_list:
                tup = ( ds['mountpoint'], ds['name'])
                ch.append(tup)   
        self.fields["dataset"] = forms.ChoiceField(choices=ch)

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
