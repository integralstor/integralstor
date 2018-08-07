import zipfile
import io
import os
import django
import django.template

from integral_view.applications.storage_insights.forms import storage_insights_forms

from integralstor.applications.storage_insights import scan_utils, query_utils
from integralstor import django_utils, config, scheduler_utils, audit, zfs, datetime_utils

query_types = [('extension_counts', 'View file count by extension', 'view_general_query_results?query_type=extension_counts'), ('files_by_extension', 'View files by extension', 'view_files_by_extension'), ('duplicates', 'View duplicate files', 'view_general_query_results?query_type=duplicate_sets'), ('newest_files', 'View most recently modified files', 'view_general_query_results?query_type=newest_files'), ('oldest_files','View files with oldest modify times', 'view_general_query_results?query_type=oldest_files'), ('largest_files', 'View largest files', 'view_general_query_results?query_type=largest_files'), ('find_files', 'Find files', 'find_files')]

def view_query_types(request):
    return_dict = {}
    global query_types
    try:
        req_params, err = django_utils.get_request_parameter_values(request, ['query_type', 'scan_configuration_id'])
        if err:
            raise Exception(err)

        configurations, err = scan_utils.get_scan_configurations(standalone=False, include_deleted=True)
        if err:
            raise Exception(err)
        if configurations:
            return_dict['configurations'] = configurations


        if request.method == "GET":

            form = storage_insights_forms.ViewQueryTypesForm(configurations = configurations, query_types = query_types)
            return_dict["form"] = form
            return django.shortcuts.render_to_response("view_query_types.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            # Form submission so create
            form = storage_insights_forms.ViewQueryTypesForm(request.POST, configurations = configurations, query_types = query_types)
            return_dict['form'] = form
            if form.is_valid():
                cd = form.cleaned_data
                query_type = cd['query_type']
                scan_configuration_id = int(cd['scan_configuration_id'])
                for q in query_types:
                    if q[0] == query_type:
                        break
                if '?' in q[2]:
                    url = '/applications/storage_insights/%s&scan_configuration_id=%d'%(q[2], scan_configuration_id)
                else:
                    url = '/applications/storage_insights/%s?scan_configuration_id=%d'%(q[2], scan_configuration_id)
                print url
                #raise Exception('a')
                return django.http.HttpResponseRedirect(url)
            else:
                return django.shortcuts.render_to_response("view_query_types.html", return_dict, context_instance=django.template.context.RequestContext(request))
        query_type = None
        if 'query_type' in req_params and req_params['query_type']:
            query_type = req_params['query_type']
        if query_type:
            if query_type not in query_types:
                raise Exception('Unknown query type. Please use the menus')
        return_dict['query_types'] = query_types
        return django.shortcuts.render_to_response('view_query_types.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_insights_base.html"
        return_dict["page_title"] = 'Select Insight type '
        return_dict['tab'] = 'query_tab'
        return_dict["error"] = 'Error loading Storage Insight types'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_general_query_results(request):
    return_dict = {}
    global query_types
    try:
        req_params, err = django_utils.get_request_parameter_values(request, ['scan_configuration_id', 'query_type', 'param1'])
        if err:
            raise Exception(err)

        if 'scan_configuration_id' not in req_params:
            raise Exception('Invalid request. Please use the menus.')
        scan_configuration_id = int(req_params['scan_configuration_id'])

        if 'query_type' not in req_params:
            raise Exception('Invalid request. Please use the menus.')
        query_type = req_params['query_type']
        
        if query_type not in ['extension_counts', 'largest_files', 'oldest_files', 'newest_files', 'duplicate_sets', 'duplicate_files']:
            raise Exception('Invalid request. Please use the menus.')

        query_type_str = ''
        for qt in query_types:
            if qt[0] == query_type:
                query_type_str = qt[1]
                break
        return_dict['query_type_str'] = query_type_str

        if query_type == 'duplicate_files':
            if 'param1' not in req_params:
                raise Exception('Invalid request. Please use the menus.')
            results, err = query_utils.get_file_info_query_results(query_type = query_type, scan_configuration_id=scan_configuration_id, param1=req_params['param1'])
        else:
            results, err = query_utils.get_file_info_query_results(query_type = query_type, scan_configuration_id=scan_configuration_id)
        if err:
            raise Exception(err)
        template = 'view_%s_results.html'%query_type
        return_dict['results'] = results
        return_dict['scan_configuration_id'] = scan_configuration_id
        return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))

    except Exception, e:
        return_dict['base_template'] = "storage_insights_base.html"
        return_dict["page_title"] = 'Storage Insights query'
        return_dict['tab'] = 'query_tab'
        return_dict["error"] = 'Error loading Storage Insight query result '
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_files_by_extension(request):
    return_dict = {}
    try:
        req_params, err = django_utils.get_request_parameter_values(request, ['scan_configuration_id', 'extension'])
        if err:
            raise Exception(err)
        if 'scan_configuration_id' not in req_params:
            raise Exception('Invalid request. Please use the menus.')
        scan_configuration_id = int(req_params['scan_configuration_id'])

        extensions, err = query_utils.get_unique_extensions(scan_configuration_id=scan_configuration_id)
        if err:
            raise Exception(err)
        configurations, err = scan_utils.get_scan_configurations(scan_configuration_id=scan_configuration_id, standalone=False, include_deleted=True)
        if err:
            raise Exception(err)

        if request.method == "GET":
            form = storage_insights_forms.GetFilesByExtensionForm(initial={'scan_configuration_id': scan_configuration_id}, extensions = extensions)
            return_dict["form"] = form
            return_dict["scan_dir"] = configurations[0]['scan_dir']
            return django.shortcuts.render_to_response("files_by_extension_form.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            # Form submission so create
            form = storage_insights_forms.GetFilesByExtensionForm(request.POST, initial={'scan_configuration_id': scan_configuration_id}, extensions = extensions)
            return_dict['form'] = form
            if form.is_valid():
                cd = form.cleaned_data
                results, err = query_utils.get_files_by_extension(scan_configuration_id=scan_configuration_id, extension = cd['extension'])
                if err:
                    raise Exception(err)
                return_dict['results'] = results
                return django.shortcuts.render_to_response("view_files_by_extension_results.html", return_dict, context_instance=django.template.context.RequestContext(request))
            else:
                return django.shortcuts.render_to_response("files_by_extension_form.html", return_dict, context_instance=django.template.context.RequestContext(request))
        
    except Exception, e:
        return_dict['base_template'] = "storage_insights_base.html"
        return_dict["page_title"] = 'Storage Insights - Extension Counts'
        return_dict['tab'] = 'query_tab'
        return_dict["error"] = 'Error loading Storage Insight information - files by extension'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def find_files(request):
    return_dict = {}
    try:
        req_params, err = django_utils.get_request_parameter_values(request, ['scan_configuration_id', 'file_name_pattern'])
        if err:
            raise Exception(err)
        if 'scan_configuration_id' not in req_params:
            raise Exception('Invalid request. Please use the menus.')
        scan_configuration_id = int(req_params['scan_configuration_id'])

        configurations, err = scan_utils.get_scan_configurations(scan_configuration_id=scan_configuration_id, standalone=False, include_deleted=True)
        if err:
            raise Exception(err)

        if request.method == "GET":
            form = storage_insights_forms.FindFilesForm(initial={'scan_configuration_id': scan_configuration_id})
            return_dict["form"] = form
            return_dict["scan_dir"] = configurations[0]['scan_dir']
            return django.shortcuts.render_to_response("find_files_form.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            # Form submission so create
            form = storage_insights_forms.FindFilesForm(request.POST, initial={'scan_configuration_id': scan_configuration_id})
            return_dict['form'] = form
            if form.is_valid():
                cd = form.cleaned_data
                results, err = query_utils.find_files(scan_configuration_id=scan_configuration_id, file_name_pattern = cd['file_name_pattern'])
                if err:
                    raise Exception(err)
                return_dict['results'] = results
                return django.shortcuts.render_to_response("view_find_files_results.html", return_dict, context_instance=django.template.context.RequestContext(request))
            else:
                return django.shortcuts.render_to_response("find_files_form.html", return_dict, context_instance=django.template.context.RequestContext(request))
        
    except Exception, e:
        return_dict['base_template'] = "storage_insights_base.html"
        return_dict["page_title"] = 'Storage Insights - Find files'
        return_dict['tab'] = 'query_tab'
        return_dict["error"] = 'Error loading Storage Insight information - find files'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def download_file(request):
    return_dict = {}
    try:

        req_params, err = django_utils.get_request_parameter_values(request, ['id'])
        if err:
            raise Exception(err)

        if 'id' not in req_params:
            raise Exception('Invalid request. Please use the menus.')

        id = req_params['id']
        file_info_row, err = query_utils.get_file_info(param = id, param_type='id')
        if err:
            raise Exception(err)
        base_name = os.path.basename(file_info_row['path'])

        zf_name = '%s.zip' % base_name
        try:
            out = io.BytesIO()
            zf = zipfile.ZipFile(out, 'w')
            zf.write(file_info_row['path'], arcname=base_name)
            zf.close()
        except Exception as e:
            raise Exception(
                "Error compressing log file : %s" % str(e))

        response = django.http.HttpResponse(
            out.getvalue(), content_type='application/x-compressed')
        response['Content-disposition'] = 'attachment; filename=%s' % (
            zf_name)

        return response
    except Exception, e:
        return_dict['base_template'] = "storage_insights_base.html"
        return_dict["page_title"] = 'Download file'
        return_dict['tab'] = 'query_tab'
        return_dict["error"] = 'Error downloading file'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_scans(request):
    return_dict = {}
    try:
        if "ack" in request.GET:
            if request.GET["ack"] == "deleted_scan":
                return_dict['ack_message'] = "Folder scan details successfully removed"

        req_params, err = django_utils.get_request_parameter_values(request, ['scan_configuration_id'])
        if err:
            raise Exception(err)

        initial = {}
        scan_configuration_id = None
        if 'scan_configuration_id' in req_params:
            if req_params['scan_configuration_id'] != 'None':
                scan_configuration_id = int(req_params['scan_configuration_id'])
                initial['scan_configuration_id'] = scan_configuration_id

        all_scans, err = scan_utils.get_scans(standalone=False)
        if err:
            raise Exception(err)
        scan_list = []
        configurations, err = scan_utils.get_scan_configurations(standalone=False, include_deleted=True)
        if err:
            raise Exception(err)
        scans = []
        for s in all_scans:
            if scan_configuration_id:
                if s['scan_configuration_id'] == scan_configuration_id:
                    scans.append(s)
            else:
                scans.append(s)
        form = storage_insights_forms.ViewScansForm(initial=initial, scan_configurations=configurations)
        return_dict['form'] = form

        return_dict['scans'] = scans
        return django.shortcuts.render_to_response('view_scans.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_insights_base.html"
        return_dict["page_title"] = 'View scans'
        return_dict['tab'] = 'view_scans_tab'
        return_dict["error"] = 'Error loading Storage Insight scans'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def delete_scan(request):
    return_dict = {}
    try:
        req_params, err = django_utils.get_request_parameter_values(request, ['scan_id'])
        if err:
            raise Exception(err)
        if 'scan_id' not in req_params:
            raise Exception('Malformed request. Please use the menus.')
        scan_id = int(req_params['scan_id'])
        scans, err = scan_utils.get_scans(scan_id=scan_id)
        if err:
            raise Exception(err)
        if not scans:
            raise Exception('Unknown scan specified. Please use the menus.')
        return_dict["scan"] = scans[0]

        if request.method == "GET":
            # Return the conf page
            return django.shortcuts.render_to_response("delete_scan_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            ret, err = scan_utils.delete_scan(scan_id)
            if err:
                raise Exception(err)

            audit_str = "Removed application Storage Insights scan details for folder '%s' run on %s" % (scans[0]['scan_dir'].lower(), scans[0]['initiate_time_str'])
            audit.audit("application_action", audit_str, request)
            return django.http.HttpResponseRedirect('/applications/storage_insights/view_scans?ack=deleted_scan')
    except Exception, e:
        return_dict['base_template'] = "storage_insights_base.html"
        return_dict["page_title"] = 'View scans'
        return_dict['tab'] = 'view_scans_tab'
        return_dict["error"] = 'Error loading Storage Insight scans'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_dashboard(request):
    return_dict = {}
    try:
        req_params, err = django_utils.get_request_parameter_values(request, ['scan_configuration_id'])
        if err:
            raise Exception(err)

        configurations, err = scan_utils.get_scan_configurations(standalone=False, include_deleted=True)
        if err:
            raise Exception(err)

        num_deleted_configurations = 0
        num_active_configurations = 0
        num_configurations = 0

        initial = {}
        scan_configuration_id = None
        if 'scan_configuration_id' in req_params:
            if req_params['scan_configuration_id'] != 'None':
                scan_configuration_id = int(req_params['scan_configuration_id'])
                initial['scan_configuration_id'] = scan_configuration_id

        selected_config = None
        for c in configurations:
            if scan_configuration_id and c['id'] == scan_configuration_id:
                selected_config = c
            if c['status_id'] == -1:
                num_deleted_configurations += 1
            else:
                num_active_configurations += 1

        if selected_config:
            scan_details = {}
            all_scans, err = scan_utils.get_scans(standalone=False)
            if err:
                raise Exception(err)
            selected_scans = []
            for scan in all_scans:
                if scan['scan_configuration_id'] == scan_configuration_id:
                    selected_scans.append(scan)
            scan_details['num_scans'] = len(selected_scans)
            latest = 0
            latest_successful = 0
            for scan in selected_scans:
                if scan['initiate_time'] > latest:
                    latest = scan['initiate_time']
                if scan['status_id'] == 2 and scan['initiate_time'] > latest_successful:
                    latest_successful = scan['initiate_time']
            if latest:
                lt, err = datetime_utils.convert_from_epoch(latest, return_format='str', str_format='%c', to='local')
                if err:
                    raise Exception(err)
                scan_details['latest_scan'] = lt
            if latest_successful:
                lt, err = datetime_utils.convert_from_epoch(latest_successful, return_format='str', str_format='%c', to='local')
                if err:
                    raise Exception(err)
                scan_details['latest_successful_scan'] = lt
            return_dict['scan_details'] = scan_details
            return_dict['selected_configuration'] = selected_config

            duplicate_sets, err = query_utils.get_duplicate_sets(scan_configuration_id)
            if err:
                raise Exception(err)
            return_dict['duplicate_sets'] = duplicate_sets

        num_configurations = num_deleted_configurations + num_active_configurations


        db_details, err = scan_utils.get_db_details()
        if err:
            raise Exception(err)
        return_dict['db_details'] = db_details
        form = storage_insights_forms.ViewConfigurationsForm(initial=initial, configurations=configurations)
        return_dict['form'] = form

        return_dict['configurations'] = configurations
        return_dict['num_deleted_configurations'] = num_deleted_configurations
        return_dict['num_active_configurations'] = num_active_configurations
        return_dict['num_configurations'] = num_configurations
        return django.shortcuts.render_to_response('view_storage_insights_dashboard.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_insights_base.html"
        return_dict["page_title"] = 'Storage Insights dashboard'
        return_dict['tab'] = 'dashboard_tab'
        return_dict["error"] = 'Error loading Storage Insight dashboard'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_scan_configurations(request):
    return_dict = {}
    try:
        if "ack" in request.GET:
            if request.GET["ack"] == "updated_scan_schedule":
                return_dict['ack_message'] = "Folder scan successfully scheduled"
            elif request.GET["ack"] == "created_scan_configuration":
                return_dict['ack_message'] = "Folder scan configuration successfully created"
            elif request.GET["ack"] == "deleted_scan_schedule":
                return_dict['ack_message'] = "Folder scan schedule successfully removed"
            elif request.GET["ack"] == "deleted_scan_configuration":
                return_dict['ack_message'] = "Folder scan configuration successfully removed"

        configurations, err = scan_utils.get_scan_configurations(standalone=False, include_deleted=True)
        if err:
            raise Exception(err)

        if configurations:
            for c in configurations:
                #print c
                if c['cron_task_id']:
                    ct_list, err = scheduler_utils.get_cron_tasks(cron_task_id=c['cron_task_id'])
                    if err:
                        raise Exception(err)
                    if ct_list:
                        c['schedule_description'] = ct_list[0]['schedule_description']
        return_dict['configurations'] = configurations
        return django.shortcuts.render_to_response('view_scan_configurations.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_insights_base.html"
        return_dict["page_title"] = 'View scan configurations'
        return_dict['tab'] = 'scan_configurations_tab'
        return_dict["error"] = 'Error loading Storage Insight scan configurations'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_scan_configuration(request):
    return_dict = {}
    try:
        datasets, err = zfs.get_all_datasets()
        if err:
            raise Exception(err)
        ds_list = []
        for dataset in datasets:
            ds_list.append(
                (dataset['properties']['mountpoint']['value'], dataset["name"]))
        req_params, err = django_utils.get_request_parameter_values(request, ['path', 'dataset'])
        if err:
            raise Exception(err)
        if 'dataset' not in req_params:
            dataset = ds_list[0][0]
        elif 'dataset' in req_params:
            dataset = req_params['dataset']
        if 'path' not in req_params:
            path = dataset
        elif 'path' in req_params:
            path = req_params['path']

        return_dict['path'] = path
        return_dict["dataset"] = ds_list

        initial = {}
        initial['path'] = path
        initial['dataset'] = dataset
        if request.method == "GET":

            form = storage_insights_forms.ScanConfigurationForm(
                dataset_list=ds_list, initial=initial)
            return_dict["form"] = form
            return django.shortcuts.render_to_response("create_scan_configuration.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            # Form submission so create
            form = storage_insights_forms.ScanConfigurationForm(
                request.POST, dataset_list=ds_list, initial=initial)
            return_dict["form"] = form
            if form.is_valid():
                cd = form.cleaned_data
                #print cd
                config_dict = {'scan_dir':cd['path'], 'exclude_dirs':cd['exclude_dirs'], 'generate_checksum':cd['generate_checksum'], 'db_transaction_size':1000, 'record_history':True}
                ret, err = scan_utils.create_scan_configuration(config_dict)
                if err:
                    raise Exception(err)
            else:
                return django.shortcuts.render_to_response("create_scan_configuration.html", return_dict, context_instance=django.template.context.RequestContext(request))

            audit_str = 'Application Storage Insights scan configuration created for scanning directory "%s"' % cd['path']
            if cd['exclude_dirs']:
                audit_str += ' but excluding directories "%s"'%cd['exclude_dirs']
            audit_str += '.'
            if cd['generate_checksum']:
                audit_str += ' File checksums enabled.'
            else:
                audit_str += ' File checksums disabled.'
            audit_str += ' Database transaction size set to %d.'%cd['db_transaction_size']
            audit.audit("application_action", audit_str, request)
            return django.http.HttpResponseRedirect('/applications/storage_insights/view_scan_configurations?ack=created_scan_configuration')
    except Exception, e:
        return_dict['base_template'] = "storage_insights_base.html"
        return_dict["page_title"] = 'Create scan configuration'
        return_dict['tab'] = 'scan_configurations_tab'
        return_dict["error"] = 'Error creating Storage Insight folder scan configuration'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def delete_scan_configuration(request):

    return_dict = {}
    try:
        type = 'mark_deleted'
        req_params, err = django_utils.get_request_parameter_values(request, ['scan_configuration_id', 'type'])
        if err:
            raise Exception(err)
        if 'scan_configuration_id' not in req_params:
            raise Exception('Malformed request. Please use the menus.')
        scan_configuration_id = int(req_params['scan_configuration_id'])
        if 'type' in req_params and req_params['type'] == 'expunge':
            type = 'expunge'
            configurations, err = scan_utils.get_scan_configurations(scan_configuration_id=scan_configuration_id, include_deleted=True)
        else:
            configurations, err = scan_utils.get_scan_configurations(scan_configuration_id=scan_configuration_id)
        if err:
            raise Exception(err)
        if not configurations:
            raise Exception('Invalid configuration specified. Please us the menus.')

        return_dict["configuration"] = configurations[0]
        return_dict["type"] = type

        if request.method == "GET":
            # Return the conf page
            return django.shortcuts.render_to_response("delete_scan_configuration_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            ret, err = scan_utils.delete_scan_configuration(configurations[0], type=type)
            if err:
                raise Exception(err)

            audit_str = "Removed application Storage Insights configuration for folder '%s'" % (configurations[0]['scan_dir'].lower())
            audit.audit("application_action", audit_str, request)
            return django.http.HttpResponseRedirect('/applications/storage_insights/view_scan_configurations?ack=deleted_scan_configuration')
    except Exception, e:
        return_dict['base_template'] = "storage_insights_base.html"
        return_dict["page_title"] = 'Remove folder scan configuration'
        return_dict['tab'] = 'scan_configurations_tab'
        return_dict["error"] = 'Error removing Storage Insight folder scan configuration'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def update_scan_schedule(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, ['scan_configuration_id', 'scheduler'])
        if err:
            raise Exception(err)
        if 'scan_configuration_id' not in req_ret:
            raise Exception('Malformed request. Please use the menus.')
        scan_configuration_id = int(req_ret['scan_configuration_id'])
        if request.method == "GET":
            # Return the conf page
            configurations, err = scan_utils.get_scan_configurations(scan_configuration_id=scan_configuration_id)
            if err:
                raise Exception(err)
            if not configurations:
                raise Exception('Invalid configuration specified. Please us the menus.')

            return_dict['configuration'] = configurations[0]
            return_dict['scan_configuration_id'] = req_ret['scan_configuration_id']
            return django.shortcuts.render_to_response("schedule_scan.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            if 'scheduler' not in req_ret:
                raise Exception("Invalid request, please use the menus.")
            scheduler = req_ret['scheduler']
            schedule = scheduler.split()
            app_root, err = config.get_application_root(app_tag='storage_insights')
            if err:
                raise Exception(err)
            cmd = 'python %s/scripts/python/storage_insights_scanner.py -d -s %d'%(app_root, scan_configuration_id)

            cron_description = 'Storage Insights scanner'
    
            cron_task_id, err = scheduler_utils.create_cron_task(
                cmd, cron_description, schedule[0], schedule[1], schedule[2], schedule[3], schedule[4], task_type_id=6)
            if err:
                raise Exception(err)
            ret, err = scan_utils.update_cron_schedule(scan_configuration_id, cron_task_id)
            if err:
                raise Exception(err)

            cron_task_list, err = scheduler_utils.get_cron_tasks(cron_task_id, task_type_id=6)
            if err:
                raise Exception(err)

            audit_str = "Application Storage Insights scan process scheduled for %s." % cron_task_list[0]['schedule_description'].lower()
            audit.audit("application_action", audit_str, request)
            return django.http.HttpResponseRedirect('/applications/storage_insights/view_scan_configurations?ack=updated_scan_schedule')
    except Exception, e:
        return_dict['base_template'] = "storage_insights_base.html"
        return_dict["page_title"] = 'Schedule folder scan'
        return_dict['tab'] = 'scan_configurations_tab'
        return_dict["error"] = 'Error scheduling Storage Insight folder scan'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def delete_scan_schedule(request):

    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, ['scan_configuration_id'])
        if err:
            raise Exception(err)
        if 'scan_configuration_id' not in req_ret:
            raise Exception('Malformed request. Please use the menus.')
        scan_configuration_id = int(req_ret['scan_configuration_id'])
        configurations, err = scan_utils.get_scan_configurations(scan_configuration_id=scan_configuration_id)
        if err:
            raise Exception(err)
        if not configurations:
            raise Exception('Invalid configuration specified. Please us the menus.')
        if not configurations[0]['cron_task_id']:
            raise Exception('The specified configuration is not currently scheduled. Please us the menus.')
        cron_task_id = configurations[0]['cron_task_id']

        cron_task_list, err = scheduler_utils.get_cron_tasks(configurations[0]['cron_task_id'], task_type_id=6)
        if err:
            raise Exception(err)
        return_dict["cron_task"] = cron_task_list[0]
        return_dict["configuration"] = configurations[0]
        return_dict["scan_configuration_id"] = scan_configuration_id

        if request.method == "GET":
            # Return the conf page
            return django.shortcuts.render_to_response("delete_scan_schedule_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            cron_description = cron_task_list[0]['description'].lower()

            ret, err = scheduler_utils.delete_cron(cron_task_id)
            if err:
                raise Exception(err)

            audit_str = "Removed application Storage Insights folder scan scheduled for %s" % (cron_task_list[0]['schedule_description'].lower())
            audit.audit("application_action", audit_str, request)
            return django.http.HttpResponseRedirect('/applications/storage_insights/view_scan_configurations?ack=deleted_scan_schedule')
    except Exception, e:
        return_dict['base_template'] = "storage_insights_base.html"
        return_dict["page_title"] = 'Remove folder scan schedule'
        return_dict['tab'] = 'scan_schedule_tab'
        return_dict["error"] = 'Error removing Storage Insight folder scan schedule'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
