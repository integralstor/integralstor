from django import forms

import os

from integral_view.core.storage.forms import folder_management_forms
from integralstor.applications.storage_insights import scan_utils

class ScanConfigurationForm(folder_management_forms.DirForm):

    generate_checksum = forms.BooleanField(required=False, initial=True)
    db_transaction_size = forms.IntegerField(initial=10000)
    exclude_dirs = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        if kwargs:
            dataset_list = kwargs.pop("dataset_list")
        super(ScanConfigurationForm, self).__init__(*args, **kwargs)

        ch = []
        if dataset_list:
            for ds in dataset_list:
                tup = (ds[0], ds[1])
                ch.append(tup)
        self.fields['dataset'] = forms.ChoiceField(
            widget=forms.Select, choices=ch)

    def clean(self):
        cd = super(ScanConfigurationForm, self).clean()
        scan_configs, err = scan_utils.get_scan_configurations()
        if err:
            raise Exception(err)
        scan_dir = cd['path'].strip().rstrip('/')
        if scan_configs:
            for sc in scan_configs:
                if scan_dir == sc['scan_dir'].strip().rstrip('/'):
                    self._errors['path'] = self.error_class(
                        ["The scan path already exists in another configuration. Please specify a unique scan path"])
                    break
        if cd['exclude_dirs']:
            components = None
            try:
                components = cd['exclude_dirs'].split(',')
            except Exception, e:
                self._errors['exclude_dirs'] = self.error_class(
                    ["Please specify a valid set of directories to exclude"])
            if components:
                ed_list = []
                for component in components:
                    if not os.path.exists('%s/%s'%(cd['path'], component.strip())):
                        self._errors['exclude_dirs'] = self.error_class(
                            ["The subdirectory '%s' does not exist. Please specify a valid set of directories to excluded"%component])
                        break
                    else:
                        ed_list.append(component)
                cd['exclude_dirs'] = ','.join(ed_list)
        return cd

class ViewScansForm(forms.Form):

    def __init__(self, *args, **kwargs):
        vl = None
        if kwargs:
            scan_configurations = kwargs.pop('scan_configurations')
        super(ViewScansForm, self).__init__(*args, **kwargs)
        ch = []
        if scan_configurations:
            ch.append((None, '--All scans--'))
            for i in scan_configurations:
                if i['status_id'] == -1:
                    tup = (i['id'], '%s - deleted'%i['scan_dir'])
                else:
                    tup = (i['id'], i['scan_dir'])
                ch.append(tup)
        self.fields['scan_id'] = forms.ChoiceField(choices=ch)

class ViewConfigurationsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        vl = None
        if kwargs:
            configs = kwargs.pop('configurations')
        super(ViewConfigurationsForm, self).__init__(*args, **kwargs)
        ch = []
        if configs:
            ch.append((None, '--Select configuration--'))
            for i in configs:
                if i['status_id'] == -1:
                    tup = (i['id'], '%s - deleted'%i['scan_dir'])
                else:
                    tup = (i['id'], i['scan_dir'])
                ch.append(tup)
        self.fields['scan_configuration_id'] = forms.ChoiceField(choices=ch)

class ViewQueryTypesForm(forms.Form):

    def __init__(self, *args, **kwargs):
        vl = None
        if kwargs:
            configurations = kwargs.pop('configurations')
            query_types = kwargs.pop('query_types')
        super(ViewQueryTypesForm, self).__init__(*args, **kwargs)
        ch = []
        if configurations:
            for i in configurations:
                if i['status_id'] == -1:
                    tup = (i['id'], '%s - deleted'%i['scan_dir'])
                else:
                    tup = (i['id'], i['scan_dir'])
                ch.append(tup)
            self.fields['scan_configuration_id'] = forms.ChoiceField(choices=ch)
        ch = []
        if query_types:
            for i in query_types:
                tup = (i[0], i[1])
                ch.append(tup)
            self.fields['query_type'] = forms.ChoiceField(choices=ch)

class GetFilesByExtensionForm(forms.Form):

    def __init__(self, *args, **kwargs):
        extensions = None

        if kwargs:
            extensions = kwargs.pop('extensions')
        super(GetFilesByExtensionForm, self).__init__(*args, **kwargs)
        ch = []
        if extensions:
            ch.append((None, '--Select extension--'))
            for i in extensions:
                if i:
                    ch.append((i,i))
                else:
                    ch.append((i, 'No extension'))
            self.fields['extension'] = forms.ChoiceField(choices=ch)
    scan_configuration_id = forms.CharField(widget=forms.HiddenInput)

class FindFilesForm(forms.Form):

    scan_configuration_id = forms.CharField(widget=forms.HiddenInput)
    file_name_pattern = forms.CharField()

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
