import django
import django.template
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

import json
import datetime

from integralstor import event_notifications, mail, audit, django_utils, inotify, alerts, system_info, iscsi_stgt, nfs, datetime_utils, cifs,  stats, services_management, zfs, command, config, networking, remote_monitoring
from integral_view.core.monitoring.forms import monitoring_forms

def view_alerts(request):
    return_dict = {}
    try:
        return_dict['base_template'] = "monitoring_base.html"
        return_dict['tab'] = 'alerts_tab'
        return_dict["page_title"] = 'Alerts'
        alerts_list, err = alerts.get_alerts()
        if err:
            raise Exception(err)
        ret, err = alerts.update_last_view_time(request)
        return_dict['alerts_list'] = alerts_list
        return django.shortcuts.render_to_response('view_alerts.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "monitoring_base.html"
        return_dict["page_title"] = 'System alerts'
        return_dict['tab'] = 'view_logs_tab'
        return_dict["error"] = 'Error loading system alerts'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def refresh_alerts(request, random=None):
    try:
        new_alerts_present, err = alerts.new_alerts_present(
            request.user.username)
        if err:
            raise Exception(err)
        if new_alerts_present:
            new_alerts = json.dumps(new_alerts_present)
            return django.http.HttpResponse(new_alerts, content_type='application/json')
        else:
            clss = "btn btn-default btn-sm"
            message = "View alerts"
            return django.http.HttpResponse("No New Alerts")
    except Exception, e:
        return django.http.HttpResponse("Error loading alerts : %s" % str(e))

def view_remote_monitoring_servers(request):
    return_dict = {}
    try:
        if "ack" in request.GET:
            if request.GET["ack"] == "updated":
                return_dict['ack_message'] = "Remote monitoring server successfully updated"
            elif request.GET["ack"] == "deleted":
                return_dict['ack_message'] = "Remote monitoring server successfully deleted"

        servers, err = remote_monitoring.get_servers()
        if err:
            raise Exception(err)
        return_dict['servers'] = servers
        return django.shortcuts.render_to_response("view_remote_monitoring_servers.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict["page_title"] = 'Remote server monitoring'
        return_dict['tab'] = 'remote_monitoring_tab'
        return_dict["error"] = 'Error loading remote monitoring server list'
        return_dict['base_template'] = "monitoring_base.html"
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_remote_monitoring_server(request):
    return_dict = {}
    try:
        if request.method == "GET":
            servers, err = remote_monitoring.get_servers()
            if err:
                raise Exception(err)
            req_ret, err = django_utils.get_request_parameter_values(request, [
                'view', 'ip'])
            if err:
                raise Exception(err)
            initial = {}
            if 'ip' in req_ret:
                ip = req_ret['ip']
                if ip in servers.keys():
                    initial['ip'] = ip
                    initial['name'] = servers[ip]['name']
                return_dict['action'] = 'update'
            else:
                return_dict['action'] = 'create'
            form = monitoring_forms.RemoteMonitoringServerForm(initial=initial)
            return_dict['form'] = form
            return django.shortcuts.render_to_response("update_remote_monitoring_server.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = monitoring_forms.RemoteMonitoringServerForm(request.POST)
            return_dict["form"] = form
            if form.is_valid():
                cd = form.cleaned_data
                res, err = remote_monitoring.update_server(
                    cd['ip'], cd['name'])
                if not res:
                    if err:
                        raise Exception(err)
                    else:
                        raise Exception(
                            'Error updating remote monitoring server list')
                audit_str = 'Updated the remote monitoring server with IP : %s and name : %s' % (
                    cd['ip'], cd['name'])
                audit.audit("update_remote_monitoring_server",
                            audit_str, request)
                return django.http.HttpResponseRedirect('/monitoring/view_remote_monitoring_servers?ack=updated')
            else:
                # invalid form
                return django.shortcuts.render_to_response("update_remote_monitoring_server.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict["page_title"] = 'Update remote server monitoring server'
        return_dict['tab'] = 'remote_monitoring_tab'
        return_dict["error"] = 'Error updating remote monitoring server'
        return_dict['base_template'] = "monitoring_base.html"
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_remote_monitoring_server(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
            'view', 'ip'])
        if err:
            raise Exception(err)
        if 'ip' not in req_ret:
            raise Exception('Invalid request, please use the menus.')
        ip = req_ret['ip']
        servers, err = remote_monitoring.get_servers()
        if err:
            raise Exception(err)
        if ip not in servers.keys():
            raise Exception(
                'Specified server is currently not being remote monitored.')
        name = servers[ip]['name']
        ret, err = remote_monitoring.delete_server(ip)
        if err:
            raise Exception(err)
        audit_str = 'Removed the remote monitoring server with IP : %s name : %s' % (
            ip, name)
        audit.audit("delete_remote_monitoring_server", audit_str, request)
        return django.http.HttpResponseRedirect('/monitoring/view_remote_monitoring_servers?ack=deleted')

    except Exception, e:
        return_dict["page_title"] = 'Remove remote server monitoring server'
        return_dict['tab'] = 'remote_monitoring_tab'
        return_dict["error"] = 'Error removing remote monitoring server'
        return_dict['base_template'] = "monitoring_base.html"
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_remote_monitoring_server_status(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
            'view', 'ip'])
        if err:
            raise Exception(err)
        if 'ip' not in req_ret:
            raise Exception('Invalid request, please use the menus.')
        status, err = remote_monitoring.get_status(req_ret['ip'])
        if err:
            raise Exception(err)
        print status
        return_dict['status'] = status
        return django.shortcuts.render_to_response("view_remote_monitoring_server_status.html", return_dict, context_instance=django.template.context.RequestContext(request))

    except Exception, e:
        return_dict["page_title"] = 'View remote server monitoring server status'
        return_dict['tab'] = 'remote_monitoring_tab'
        return_dict["error"] = 'Error viewing remote monitoring server status'
        return_dict['base_template'] = "monitoring_base.html"
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def api_get_status(request):
    si = {}
    err = None
    try:
        si, err = system_info.load_system_config()
        # print si
        if err:
            raise Exception(err)
    except Exception, e:
        # print str(e)
        return JsonResponse({'error': str(e)})
        # return django.http.HttpResponse({'error': str(e)}
        # ,content_type='application/json')
    else:
        return JsonResponse(si)
        # return django.http.HttpResponse(si,content_type='application/json')


def view_read_write_stats(request):
    return_dict = {}
    try:

        req_params, err = django_utils.get_request_parameter_values(
            request, ['last_x_seconds', 'refresh_interval'])
        if err:
            raise Exception(err)
        if 'refresh_interval' in req_params:
            return_dict['refresh_interval'] = req_params['refresh_interval']
        if 'last_x_seconds' in req_params:
            actions = ['access', 'modify', 'create', 'delete', 'move']
            count_dict = {}
            for action in actions:
                count, err = inotify.get_count(
                    action, int(req_params['last_x_seconds']))
                if err:
                    raise Exception(err)
                count_dict[action] = count
            # print count_dict
            return_dict['count_dict'] = count_dict
            return_dict['last_x_seconds'] = int(req_params['last_x_seconds'])
            return_dict['last_x_minutes'] = int(
                req_params['last_x_seconds']) / 60

        lines, err = command.get_command_output('/usr/bin/arc_summary.py -d')
        if not err:
            return_dict['arc_summary_lines'] = lines
        else:
            return_dict['arc_error'] = err

        lines, err = command.get_command_output('zpool iostat -T d -v')
        if not err:
            return_dict['zpool_iostat_lines'] = lines
        else:
            return_dict['zpool_iostat_error'] = err

        lines, err = command.get_command_output('iostat -dm')
        if not err:
            return_dict['iostat_lines'] = lines
        else:
            return_dict['iostat_error'] = err

        lines, err = command.get_command_output('iostat -c')
        if not err:
            return_dict['cpu_iostat_lines'] = lines
        else:
            return_dict['cpu_iostat_error'] = err

        lines, err = command.get_command_output('free -h')
        if not err:
            return_dict['mem_lines'] = lines
        else:
            return_dict['mem_error'] = err

        lines, err = command.get_command_output('free -h')
        if not err:
            return_dict['mem_lines'] = lines
        else:
            return_dict['mem_error'] = err

        if err:
            raise Exception(err)
        return django.shortcuts.render_to_response('view_read_write_stats.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "monitoring_base.html"
        return_dict["page_title"] = 'Monitoring'
        return_dict['tab'] = 'dir_manager_tab'
        return_dict["error"] = 'Error loading read and write stats'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

@login_required
def view_dashboard(request, page = None):
    return_dict = {}
    try:
        return_dict["page_title"] = 'Overall system health'
        return_dict['tab'] = 'system_health_tab'
        return_dict["error"] = 'Error loading system health data'

        if request.method != 'GET':
            raise Exception('Invalid access method. Please use the menus')

        si, err = system_info.load_system_config()
        if err:
            raise Exception(err)
        if not si:
            raise Exception('Error loading system configuration')

        #node_name = si.keys()[0]
        #node = si[node_name]
        return_dict['node'] = si
        # print node.keys()

        # By default show error page
        template = "logged_in_error.html"

        # Chart specific declarations
        # will return 02, instead of 2.
        end_epoch, err = datetime_utils.get_epoch(when='now')
        if err:
            raise Exception(err)
        start_epoch = end_epoch - 3 * 60 * 60
        start, err = datetime_utils.convert_from_epoch(
            start_epoch, return_format='str', str_format='%H:%M:%S', to='local')
        if err:
            raise Exception(err)
        end, err = datetime_utils.convert_from_epoch(
            end_epoch, return_format='str', str_format='%H:%M:%S', to='local')
        if err:
            raise Exception(err)

        todays_date = (datetime.date.today()).strftime('%02d')

        value_list = []
        time_list = []

        num_bad_disks = 0
        num_hw_raid_bad_disks = 0
        num_hw_raid_ctrl_disks = 0
        num_smart_ctrl_disks = 0
        num_disks = len(si['disks'])
        disks_ok = True
        for sn, disk in si['disks'].items():
            if 'status' in disk:
                if 'hw_raid' in disk:
                    if not disk['hw_raid']:
                        num_smart_ctrl_disks += 1
                        if (disk['status'] is not None and disk['status'].upper() not in ['PASSED', 'OK']):
                            num_bad_disks += 1
                            disks_ok = False
                    else:
                        num_hw_raid_ctrl_disks += 1
                        if (disk['status'] is not None and disk['status'].upper() != 'OK'):
                            num_hw_raid_bad_disks += 1
                            disks_ok = False
                else:
                    # Assume its a non raid disk
                    num_smart_ctrl_disks += 1
                    if (disk['status'] is not None and disk['status'].upper() not in ['PASSED', 'OK']):
                        num_bad_disks += 1
                        disks_ok = False

        return_dict['num_disks'] = num_disks
        return_dict['num_bad_disks'] = num_bad_disks
        return_dict['disks_ok'] = disks_ok
        return_dict['num_hw_raid_bad_disks'] = num_hw_raid_bad_disks
        return_dict['num_hw_raid_ctrl_disks'] = num_hw_raid_ctrl_disks
        return_dict['num_smart_ctrl_disks'] = num_smart_ctrl_disks

        if 'ipmi_status' in si:
            num_sensors = len(si['ipmi_status'])
            num_bad_sensors = 0
            ipmi_ok = True
            for sensor in si['ipmi_status']:
                if sensor['status'] in ['ok', 'nr', 'na']:
                    continue
                else:
                    num_bad_sensors += 1
                    ipmi_ok = False
            return_dict['num_sensors'] = num_sensors
            return_dict['num_bad_sensors'] = num_bad_sensors
            return_dict['ipmi_ok'] = ipmi_ok

        services_dict, err = services_management.get_sysd_services_status()
        if err:
            raise Exception(err)

        num_services = len(services_dict)
        num_failed_services = 0
        num_active_services = 0
        num_inactive_services = 0
        services_ok = True

        if services_dict:
            for service, service_d in services_dict.items():
                if service_d["info"]["status"]["status_str"] == "Active":
                    num_active_services += 1
                elif service_d["info"]["status"]["status_str"] == "Inactive":
                    num_inactive_services += 1
                elif service_d["info"]["status"]["status_str"] == "Failed":
                    num_failed_services += 1
                    services_ok = False
                elif service_d["info"]["status"]["status_str"] == "Unknown State":
                    num_failed_services += 1
                    services_ok = False
            return_dict['num_services'] = num_services
            return_dict['num_active_services'] = num_active_services
            return_dict['num_inactive_services'] = num_inactive_services
            return_dict['num_failed_services'] = num_failed_services
            return_dict['services_ok'] = services_ok
        else:
            raise Exception('Error retrieving services status')

        pools, err = zfs.get_pools()
        if err:
            raise Exception(err)

        num_pools = len(pools)
        num_bad_pools = 0
        num_degraded_pools = 0
        num_high_usage_pools = 0
        for pool in pools:
            if pool['usage']['used_percent'] > 75:
                num_high_usage_pools += 1
            if pool['config']['pool']['root']['status']['state'] == 'ONLINE':
                pass
            elif pool['config']['pool']['root']['status']['state'] == 'DEGRADED':
                num_degraded_pools += 1
            else:
                num_bad_pools += 1
        return_dict['num_pools'] = num_pools
        return_dict['num_bad_pools'] = num_bad_pools
        return_dict['num_degraded_pools'] = num_degraded_pools
        return_dict['num_high_usage_pools'] = num_high_usage_pools

        load_avg_ok = True
        if (si["load_avg"]["5_min"] > si["load_avg"]["cpu_cores"]) or (si["load_avg"]["15_min"] > si["load_avg"]["cpu_cores"]):
            load_avg_ok = False
        return_dict['load_avg_ok'] = load_avg_ok

        shares_list, err = cifs.get_shares_list()
        if err:
            raise Exception(err)
        return_dict['num_cifs_shares'] = len(shares_list)

        exports_list, err = nfs.load_exports_list()
        if err:
            raise Exception(err)
        return_dict['num_nfs_exports'] = len(exports_list)

        target_list, err = iscsi_stgt.get_targets()
        if err:
            raise Exception(err)
        return_dict['num_iscsi_targets'] = len(target_list)

        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_str = '%s hours' % (
                ':'.join(str(datetime.timedelta(seconds=uptime_seconds)).split(':')[:2]))
            return_dict['uptime_str'] = uptime_str

        # CPU status
        if not page:
            page = "sys_health"
        if page == "cpu":
            return_dict["page_title"] = 'CPU statistics'
            return_dict['tab'] = 'cpu_tab'
            return_dict["error"] = 'Error loading CPU statistics'
            cpu, err = stats.get_system_stats(todays_date, start, end, "cpu")
            if err:
                raise Exception(err)
            value_dict = {}
            if cpu:
                for key in cpu.keys():
                    value_list = []
                    time_list = []
                    if key == "date":
                        pass
                    else:
                        if cpu[key]:
                            for a in cpu[key]:
                                time_list.append(a[0])
                                value_list.append(a[1])
                        value_dict[key] = value_list
            return_dict["data_dict"] = value_dict
            queue, err = stats.get_system_stats(
                todays_date, start, end, "queue")
            if err:
                raise Exception(err)
            value_dict = {}
            if queue:
                for key in queue.keys():
                    value_list = []
                    time_list = []
                    if key == "date":
                        pass
                    else:
                        for a in queue[key]:
                            time_list.append(a[0])
                            value_list.append(a[1])
                        value_dict[key] = value_list
            return_dict["data_dict_queue"] = value_dict
            return_dict['node'] = si
            d = {}
            template = "view_cpu_stats.html"
        elif page == "sys_health":
            return_dict["page_title"] = 'Overall system health'
            return_dict['tab'] = 'system_health_tab'
            return_dict["error"] = 'Error loading system health data'
            template = "view_dashboard.html"
            hw_platform, err = config.get_hardware_platform()
            if hw_platform:
                return_dict['hw_platform'] = hw_platform
                if hw_platform == 'dell':
                    from integralstor.platforms import dell
                    idrac_url, err = dell.get_idrac_addr()
                    if idrac_url:
                        return_dict['idrac_url'] = idrac_url
        # Memory
        elif page == "memory":
            return_dict["page_title"] = 'Memory statistics'
            return_dict['tab'] = 'memory_tab'
            return_dict["error"] = 'Error loading memory statistics'
            mem, err = stats.get_system_stats(
                todays_date, start, end, "memory")
            if err:
                raise Exception(err)
            if mem:
                for a in mem["memused"]:
                    time_list.append(a[0])
                    value_list.append((a[1] / (1024 * 1024)))
            return_dict['memory_status'] = si['memory']
            template = "view_memory_stats.html"
        # Network
        elif page == "network":
            return_dict["page_title"] = 'Network statistics'
            return_dict['tab'] = 'network_tab'
            return_dict["error"] = 'Error loading Network statistics'
            network, err = stats.get_system_stats(
                todays_date, start, end, "network")
            if err:
                raise Exception(err)
            value_dict = {}
            if network:
                for key in network.keys():
                    value_list = []
                    time_list = []
                    if key == "date" or key == "lo":
                        pass
                    else:
                        for a in network[key]["ifutil-percent"]:
                            time_list.append(a[0])
                            value_list.append(a[1])
                        value_dict[key] = value_list

            return_dict["data_dict"] = value_dict
            return_dict["network_status"] = si['interfaces']
            template = "view_network_stats.html"
        return_dict["labels"] = time_list
        return_dict["data"] = value_list
        return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "monitoring_base.html"
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
