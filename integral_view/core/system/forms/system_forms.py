from django import forms
import pytz
import datetime
from integralstor import networking

from integral_view.forms import common_forms

class ConfigureNTPForm(forms.Form):

    server_list = common_forms.MultipleServerField()

class ConfigureEmailForm(forms.Form):

    server = forms.CharField(required=True)
    port = forms.IntegerField(required=True)
    username = forms.CharField(required=True)
    pswd = forms.CharField(widget=forms.PasswordInput())
    tls = forms.BooleanField(required=False)
    rcpt_list = common_forms.MultipleEmailField(required=False)

class DateTimeForm(forms.Form):
    system_time = forms.CharField(required=False)
    system_date = forms.CharField(required=False)
    system_timezone = forms.ChoiceField(choices=[(item, item + ' ' + datetime.datetime.now(
        pytz.timezone(item)).strftime('%Z (GMT%z)')) for item in pytz.common_timezones], required=False)

    def clean(self):
        cd = super(DateTimeForm, self).clean()
        if ('system_time' not in cd or cd['system_time'] == '') and ('system_date' not in cd or cd['system_date'] == '') and ('system_timezone' not in cd or cd['system_timezone'] == ''):
            raise forms.ValidationError(
                "Atleast date, time or timezone should be present")
        else:
            if 'system_date' in cd:
                if cd['system_date'] == '':
                    cd['system_date'] = None
            if 'system_time' in cd:
                if cd['system_time'] == '':
                    cd['system_time'] = None
            if 'system_timezone' in cd:
                if cd['system_timezone'] == '':
                    cd['system_timezone'] = None
            return cd

class AlertNotificationsForm(forms.Form):
    recipient_list = common_forms.MultipleEmailField()

    def __init__(self, *args, **kwargs):
        reference_subsystem_types = None
        reference_severity_types = None
        reference_notification_types = None
        if kwargs and 'reference_subsystem_types' in kwargs:
            reference_subsystem_types = kwargs.pop('reference_subsystem_types')
        if kwargs and 'reference_severity_types' in kwargs:
            reference_severity_types = kwargs.pop('reference_severity_types')
        if kwargs and 'reference_notification_types' in kwargs:
            reference_notification_types = kwargs.pop(
                'reference_notification_types')
        super(AlertNotificationsForm,
              self).__init__(*args, **kwargs)
        ch = []
        if reference_subsystem_types:
            for id, description in reference_subsystem_types.items():
                if id == -1:
                    continue
                ch.append((id, description))
        self.fields['subsystem_type_id'] = forms.ChoiceField(choices=ch)
        ch = []
        if reference_severity_types:
            for id, description in reference_severity_types.items():
                if id == -1:
                    continue
                ch.append((id, description))
        self.fields['severity_type_id'] = forms.ChoiceField(choices=ch)
        ch = []
        if reference_notification_types:
            for id, description in reference_notification_types.items():
                ch.append((id, description))
        self.fields['notification_type_id'] = forms.ChoiceField(choices=ch)

    def clean(self):
        cd = super(AlertNotificationsForm, self).clean()
        # print 'form cd', cd
        if int(cd['notification_type_id']) == 1:
            if 'recipient_list' not in cd or (not cd['recipient_list']):
                self._errors["recipient_list"] = self.error_class(
                    ["The recipient list is required."])
        return cd


class AuditNotificationsForm(forms.Form):
    recipient_list = common_forms.MultipleEmailField()

    def __init__(self, *args, **kwargs):
        reference_notification_types = None
        if kwargs and 'reference_notification_types' in kwargs:
            reference_notification_types = kwargs.pop(
                'reference_notification_types')
        super(AuditNotificationsForm,
              self).__init__(*args, **kwargs)
        ch = []
        if reference_notification_types:
            for id, description in reference_notification_types.items():
                ch.append((id, description))
        self.fields['notification_type_id'] = forms.ChoiceField(choices=ch)

    def clean(self):
        cd = super(AuditNotificationsForm, self).clean()
        # print 'form cd', cd
        if int(cd['notification_type_id']) == 1:
            if 'recipient_list' not in cd or (not cd['recipient_list']):
                self._errors["recipient_list"] = self.error_class(
                    ["The recipient list is required."])
        return cd


class LogNotificationsForm(forms.Form):
    recipient_list = common_forms.MultipleEmailField()

    def __init__(self, *args, **kwargs):
        reference_notification_types = None
        if kwargs and 'reference_notification_types' in kwargs:
            reference_notification_types = kwargs.pop(
                'reference_notification_types')
        reference_event_subtypes = None
        if kwargs and 'reference_event_subtypes' in kwargs:
            reference_event_subtypes = kwargs.pop('reference_event_subtypes')
        super(LogNotificationsForm,
              self).__init__(*args, **kwargs)
        ch = []
        if reference_notification_types:
            for id, description in reference_notification_types.items():
                ch.append((id, description))
        self.fields['notification_type_id'] = forms.ChoiceField(choices=ch)

        ch = []
        if reference_event_subtypes:
            for res in reference_event_subtypes:
                if res['event_type_id'] != 3:
                    continue
                ch.append((res['event_subtype_id'], res['description']))
        self.fields['event_subtype_id'] = forms.ChoiceField(choices=ch)

    def clean(self):
        cd = super(LogNotificationsForm, self).clean()
        # print 'form cd', cd
        if int(cd['notification_type_id']) == 1:
            if 'recipient_list' not in cd or (not cd['recipient_list']):
                self._errors["recipient_list"] = self.error_class(
                    ["The recipient list is required."])
        return cd



class OrgInfoForm(forms.Form):
    org_name = forms.CharField(required=False)
    unit_name = forms.CharField(required=False)
    unit_id = forms.CharField(required=False)
    subunit_name = forms.CharField(required=False)
    subunit_id = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        initial = None
        if kwargs:
            if 'initial' in kwargs:
                initial = kwargs.pop('initial')
        super(OrgInfoForm, self).__init__(*args, **kwargs)
        if initial:
            if initial['org_name']:
                self.fields['org_name'] = forms.CharField(
                    required=False, initial=str(initial['org_name']))
            if initial['unit_name']:
                self.fields['unit_name'] = forms.CharField(
                    required=False, initial=str(initial['unit_name']))
            if initial['unit_id']:
                self.fields['unit_id'] = forms.CharField(
                    required=False, initial=str(initial['unit_id']))
            if initial['subunit_name']:
                self.fields['subunit_name'] = forms.CharField(
                    required=False, initial=str(initial['subunit_name']))
            if initial['subunit_id']:
                self.fields['subunit_id'] = forms.CharField(
                    required=False, initial=str(initial['subunit_id']))

    def clean(self):
        cd = super(OrgInfoForm, self).clean()
        org_name = str(cd.get('org_name')).strip()
        unit_name = str(cd.get('unit_name')).strip()
        unit_id = str(cd.get('unit_id')).strip()
        subunit_name = str(cd.get('subunit_name')).strip()
        subunit_id = str(cd.get('subunit_id')).strip()
        # Though the fields are not mandatory, accept only if atleast one field
        # has a character value
        if (org_name == '') and (unit_name == '') and (unit_id == '') and (subunit_name == '') and (subunit_id == ''):
            raise forms.ValidationError(
                'Please provide a value for atleast one of the fields')
        return self.cleaned_data


class FactoryDefaultsForm(forms.Form):
    delete_cifs_shares = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class shares_class'}), required=False)
    delete_nfs_exports = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class shares_class'}), required=False)
    delete_rsync_shares = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class shares_class'}), required=False)
    delete_iscsi_targets = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class shares_class'}), required=False)

    delete_org_info = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class others'}), required=False)

    delete_local_users = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class users_groups_class'}), required=False)
    delete_local_groups = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class users_groups_class'}), required=False)

    delete_dns_settings = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class networking_class'}), required=False)
    delete_network_interface_settings = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class networking_class'}), required=False)
    delete_network_bonds = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class networking_class'}), required=False)
    delete_network_vlans = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class networking_class'}), required=False)
    reset_hostname = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class networking_class'}), required=False)
    default_ip = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class networking_class'}), required=False)

    delete_ssl_certificates = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class ssl_ssh_class'}), required=False)
    delete_ssh_authorized_keys = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class ssl_ssh_class'}), required=False)
    delete_ssh_fingerprints = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class ssl_ssh_class'}), required=False)

    delete_audits = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class logs_class'}), required=False)
    delete_alerts = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class logs_class'}), required=False)
    delete_logs = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class logs_class'}), required=False)

    delete_remote_replications = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class replication_tasks_class'}), required=False)
    delete_tasks_and_logs = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class replication_tasks_class'}), required=False)

    reset_cifs_settings = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class services_class'}), required=False)
    reset_ntp_settings = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class services_class'}), required=False)
    reset_ftp_settings = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class services_class'}), required=False)
    delete_email_settings = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class services_class'}), required=False)

    delete_zfs_pools = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'data_class zfs_class'}), required=False)
    delete_zfs_datasets_and_snapshots = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'data_class zfs_class'}), required=False)
    delete_zfs_zvols_and_snapshots = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'data_class zfs_class'}), required=False)

    def clean_default_ip(self):
        is_default_ip = self.cleaned_data['default_ip']
        is_delete_nic = self.cleaned_data['delete_network_interface_settings']
        is_delete_bonds = self.cleaned_data['delete_network_bonds']
        if is_default_ip is True:
            if (is_delete_nic and is_delete_bonds) is not True:
                self._errors['delete_network_interface_settings'] = self.error_class(
                    ["This should be selected if default IP must be set on reboot"])
                self._errors['delete_network_bonds'] = self.error_class(
                    ["This should be selected if default IP must be set on reboot"])
        return is_default_ip

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
