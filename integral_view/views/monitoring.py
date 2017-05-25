import django
import django.template
import django.utils.timezone
import time, datetime
from django.http import HttpResponse

from integralstor_utils import django_utils, config, inotify, system_date_time, command


def view_read_write_stats(request):
    return_dict = {}
    try:

        req_params, err = django_utils.get_request_parameter_values(request, ['last_x_seconds', 'refresh_interval'])
        if err:
            raise Exception(err)
        if 'refresh_interval' in req_params:
            return_dict['refresh_interval'] = req_params['refresh_interval']
        if 'last_x_seconds' in req_params:
            actions = ['access', 'modify', 'create', 'delete', 'move']
            count_dict = {}
            for action in actions:
                count, err = inotify.get_count(action, int(req_params['last_x_seconds']))
                if err:
                    raise Exception(err)
                count_dict[action] = count
            #print count_dict
            return_dict['count_dict'] = count_dict
            return_dict['last_x_seconds'] = int(req_params['last_x_seconds'])
            return_dict['last_x_minutes'] = int(req_params['last_x_seconds'])/60

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

        '''
        local_timezone, err = system_date_time.get_current_timezone()
        if err:
            raise Exception(err)
        if 'timezone_str' not in local_timezone:
            timezone_str = 'UTC'
        else:
            timezone_str = local_timezone['timezone_str']

        tz = pytz.timezone(timezone_str)
        django.utils.timezone.activate(tz)
        now_local = datetime.datetime.now(tz)

        now = int(now_local.strftime('%s'))
        '''
        if err:
            raise Exception(err)
        return django.shortcuts.render_to_response('view_read_write_stats.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "system_base.html"
        return_dict["page_title"] = 'Monitoring'
        return_dict['tab'] = 'dir_manager_tab'
        return_dict["error"] = 'Error loading read and write stats'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
