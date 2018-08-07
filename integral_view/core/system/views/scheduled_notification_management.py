import django
import django.template
from django.http import HttpResponse
from integralstor import event_notifications, mail, audit, django_utils, alerts
from integralstor import config

from integral_view.core.system.forms import system_forms


def view_scheduled_notifications(request):
    return_dict = {}
    try:
        if "ack" in request.GET:
            if request.GET["ack"] == "deleted":
                return_dict['ack_message'] = "Scheduled notification successfully removed"
            elif request.GET["ack"] == "created":
                return_dict['ack_message'] = "Scheduled notification successfully created"

        ent_list, err = event_notifications.get_event_notification_triggers()
        # print ent_list
        if err:
            raise Exception(err)
        for ent in ent_list:
            if ent['notification_type_id'] == 1:
                enc, err = mail.get_event_notification_configuration(
                    ent['enc_id'])
                if err:
                    raise Exception(err)
                if enc:
                    ent['recipient_list'] = enc['recipient_list']

        return_dict['ent_list'] = ent_list
        return django.shortcuts.render_to_response("view_scheduled_notifications.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict["page_title"] = 'View scheduled notifications'
        return_dict['tab'] = 'scheduled_notifications_tab'
        return_dict["error"] = 'Error loading scheduled notifications list'
        return_dict['base_template'] = "system_base.html"
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_scheduled_notification(request):
    return_dict = {}
    try:
        req_params, err = django_utils.get_request_parameter_values(request, [
            'event_type_id', 'scheduler'])
        if err:
            raise Exception(err)

        reference_table_entries, err = event_notifications.get_reference_table_entries(
            ['reference_event_types', 'reference_event_subtypes', 'reference_notification_types', 'reference_severity_types', 'reference_subsystem_types'])
        if err:
            raise Exception(err)
        if 'event_type_id' not in req_params or int(req_params['event_type_id']) not in reference_table_entries['reference_event_types'].keys():
            raise Exception('Invalid request. Please use the menus.')
        return_dict['event_type_id'] = req_params['event_type_id']
        event_type_id = int(req_params['event_type_id'])
        if request.method == "GET":
            if event_type_id == 1:
                form = system_forms.AlertNotificationsForm(reference_subsystem_types=reference_table_entries['reference_subsystem_types'], reference_severity_types=reference_table_entries[
                                                               'reference_severity_types'], reference_notification_types=reference_table_entries['reference_notification_types'])
                template = 'create_alert_notification.html'
            elif event_type_id == 2:
                form = system_forms.AuditNotificationsForm(
                    reference_notification_types=reference_table_entries['reference_notification_types'])
                template = 'create_audit_notification.html'
            elif event_type_id == 3:
                form = system_forms.LogNotificationsForm(
                    reference_notification_types=reference_table_entries['reference_notification_types'], reference_event_subtypes=reference_table_entries['reference_event_subtypes'])
                template = 'create_report_notification.html'
            return_dict['form'] = form
            return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))

        elif request.method == "POST":
            scheduler = req_params['scheduler']
            schedule = scheduler.split()
            if event_type_id == 1:
                form = system_forms.AlertNotificationsForm(request.POST, reference_subsystem_types=reference_table_entries['reference_subsystem_types'], reference_severity_types=reference_table_entries[
                                                               'reference_severity_types'], reference_notification_types=reference_table_entries['reference_notification_types'])
                template = 'create_alert_notification.html'
            elif event_type_id == 2:
                form = system_forms.AuditNotificationsForm(
                    request.POST, reference_notification_types=reference_table_entries['reference_notification_types'])
                template = 'create_audit_notification.html'
            elif event_type_id == 3:
                form = system_forms.LogNotificationsForm(request.POST, reference_notification_types=reference_table_entries[
                                                             'reference_notification_types'], reference_event_subtypes=reference_table_entries['reference_event_subtypes'])
                template = 'create_report_notification.html'
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data

            psp, err = config.get_python_scripts_path()
            if err:
                raise Exception(err)
            if 'subsystem_type_id' in cd:
                subsystem_type_id = int(cd['subsystem_type_id'])
            else:
                subsystem_type_id = -1
            if 'event_subtype_id' in cd:
                event_subtype_id = int(cd['event_subtype_id'])
            else:
                event_subtype_id = -1
            if 'severity_type_id' in cd:
                severity_type_id = int(cd['severity_type_id'])
            else:
                severity_type_id = -1
            if int(cd['notification_type_id']) == 1:
                enc_id, err = mail.create_event_notification_configuration(
                    cd['recipient_list'])
                if err:
                    raise Exception(err)
            audit_str, err = event_notifications.create_event_notification(schedule, event_type_id, event_subtype_id, subsystem_type_id, int(
                cd['notification_type_id']), severity_type_id, enc_id, reference_table_entries=reference_table_entries)
            if err:
                if int(cd['notification_type_id']) == 1:
                    mail.delete_event_notification_configuration(enc_id)
                raise Exception(err)

            if int(cd['notification_type_id']) == 1:
                audit_str += " Emails will be sent to %s" % cd['recipient_list']

            if event_type_id == 1:
                audit.audit("create_alert_notification", audit_str, request)
            elif event_type_id == 2:
                audit.audit("create_audit_notification", audit_str, request)
            elif event_type_id == 3:
                audit.audit("create_report_notification", audit_str, request)

            return django.http.HttpResponseRedirect('/system/view_scheduled_notifications?ack=created')
    except Exception, e:
        return_dict["page_title"] = 'Crete scheduled notification'
        return_dict['tab'] = 'scheduled_notifications_tab'
        return_dict["error"] = 'Error creating scheduled notification'
        return_dict['base_template'] = "system_base.html"
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_scheduled_notification(request):
    return_dict = {}
    try:
        req_params, err = django_utils.get_request_parameter_values(request, [
            'ent_id'])
        if err:
            raise Exception(err)
        if 'ent_id' not in req_params:
            raise Exception('Invalid request, please use the menus.')
        ent_id = int(req_params['ent_id'])
        ent, err = event_notifications.get_event_notification_trigger(ent_id)
        # print ent
        if err:
            raise Exception(err)
        ret, err = event_notifications.delete_event_notification(ent_id)
        if err:
            raise Exception(err)
        audit_str = 'Removed the event notification: %s, that was scheduled for %s' % (
            ent['description'], ent['schedule_description'])
        if ent['event_type_id'] == 1:
            audit.audit("delete_alert_notification", audit_str, request)
        elif ent['event_type_id'] == 2:
            audit.audit("delete_audit_notification", audit_str, request)
        elif ent['event_type_id'] == 3:
            audit.audit("delete_report_notification", audit_str, request)
        return django.http.HttpResponseRedirect('/system/view_scheduled_notifications?ack=deleted')
    except Exception, e:
        return_dict["page_title"] = 'Remove scheduled notification'
        return_dict['tab'] = 'scheduled_notifications_tab'
        return_dict["error"] = 'Error removing scheduled notification'
        return_dict['base_template'] = "system_base.html"
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

