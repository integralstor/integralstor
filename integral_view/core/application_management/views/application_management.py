import django.template
import django
from django.contrib.auth.decorators import login_required
from integralstor import django_utils
import django.http

applications = {'urbackup': {'name':'Endpoint/Server backup', 'provider_name':'URBackup', 'provider_url':'https://urbackup.org', 'use_launch_url_prefix':True, 'launch_url_port': 55414, 'launch_url_path': None}, 'storage_insights':{'name':'Storage Insights', 'provider_name':'Fractalio Data', 'provider_url':'https://fractalio.com', 'use_launch_url_prefix':False, 'launch_url_path': 'applications/storage_insights'}}

def view_applications(request):
    return_dict = {}
    try:
        if "ack" in request.GET:
            if request.GET["ack"] == "deleted":
                return_dict['ack_message'] = "Scheduled task successfully removed"
            if request.GET["ack"] == "modified":
                return_dict['ack_message'] = "Scheduled task successfully modified"

        return_dict["applications"] = applications
        return django.shortcuts.render_to_response("view_applications.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "application_management_base.html"
        return_dict["page_title"] = 'Installed applications'
        return_dict['tab'] = 'view_applications_tab'
        return_dict["error"] = 'Error retriving installed applications'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def launch_application(request):
    return_dict = {}
    try:
        req_params, err = django_utils.get_request_parameter_values(request, [
                                                                 'app_tag'])
        if err:
            raise Exception(err)
        if 'app_tag' not in req_params:
            raise Exception("Invalid request, please use the menus.")
        if req_params['app_tag'] not in applications.keys():
            raise Exception("Invalid application, please use the menus.")
        application = applications[req_params['app_tag']]
        

        url = ''
        if 'use_launch_url_prefix' in application and application['use_launch_url_prefix']:
            if 'launch_url_protocol' in application:
                url = '%s:'%application['launch_url_protocol']
            else:
                url = 'http:'
            if 'launch_url_host' in application and application['launch_url_host']:
                host = application['launch_url_host']
            else:
                host = request.META['HTTP_HOST']
                if ':' in host:
                    col_pos = host.find(':')
                    if col_pos:
                        host = host[:col_pos]
                url = '%s//%s'%(url, host)
            if 'launch_url_port' in application and application['launch_url_port']:
                url = '%s:%s'%(url, application['launch_url_port'])
        if 'launch_url_path' in application and application['launch_url_path']:
            url = '%s/%s'%(url, application['launch_url_path'])
        #print url
        
        return_dict["application"] = application
        return_dict["url"] = url
        return django.shortcuts.render_to_response("application_launcher.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        print 'exception', e
        return_dict['base_template'] = "application_management_base.html"
        return_dict["page_title"] = 'Application'
        return_dict['tab'] = 'applications_tab'
        return_dict["error"] = 'Error launching application'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
