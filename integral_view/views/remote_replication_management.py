import django
import django.template

from integralstor_common import zfs, audit, common, remote_replication, scheduler_utils


def view_remote_replications(request):
    return_dict = {}
    try:
        if "ack" in request.GET:
            if request.GET["ack"] == "cancelled":
                return_dict['ack_message'] = 'Selected replication successfully cancelled.'
            elif request.GET["ack"] == "created":
                return_dict['ack_message'] = 'Replication successfully scheduled.'
            elif request.GET["ack"] == "updated":
                return_dict['ack_message'] = 'Selected replication parameters successfully updated.'

        replications, err = remote_replication.get_remote_replications()
        if err:
            raise Exception(err)
        return_dict["replications"] = replications
        return django.shortcuts.render_to_response('view_remote_replications.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception as e:
        return_dict['base_template'] = "snapshot_replication_base.html"
        return_dict["page_title"] = 'View Remote Replication'
        return_dict['tab'] = 'view_remote_replications_tab'
        return_dict["error"] = 'Error retreiving replication informat'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_remote_replication(request):
    return_dict = {}
    try:

        if request.method == "GET":
            datasets = []
            pools, err = zfs.get_all_datasets_and_pools()
            if err:
                raise Exception(err)
            for pool in pools:
                if "/" in pool:
                    datasets.append(pool)
            return_dict["datasets"] = datasets
            return django.shortcuts.render_to_response('update_remote_replication.html', return_dict, context_instance=django.template.context.RequestContext(request))

        elif request.method == "POST":
            source_dataset = request.POST.get('source_dataset')
            scheduler = request.POST.get('scheduler')
            schedule = scheduler.split()
            destination_ip = request.POST.get('destination_ip')
            destination_pool = request.POST.get('destination_pool')
            destination_username = "replicator"

            if (not destination_ip) or (not destination_pool) or (not source_dataset):
                raise Exception("Incomplete request.")

            existing_repl, err = remote_replication.get_remote_replications_with(
                source_dataset, destination_ip, destination_pool)
            print existing_repl
            if err:
                raise Exception(err)
            if existing_repl:
                raise Exception(
                    "A replication schedule already exists with matching entires/options.")

            py_scripts_path, err = common.get_python_scripts_path()
            if err:
                raise Exception(err)

            cmd = '%s/add_remote_replication_task.py %s %s %s %s' % (
                py_scripts_path, source_dataset, destination_ip, destination_username, destination_pool)
            description = 'Replication of %s to pool %s on machine %s' % (
                source_dataset, destination_pool, destination_ip)
            cron_task_id, err = scheduler_utils.add_cron_task(
                cmd, description, schedule[0], schedule[1], schedule[2], schedule[3], schedule[4])
            if err:
                raise Exception(err)

            remote_replication_id, err = remote_replication.add_remote_replication(
                source_dataset, destination_ip, destination_username, destination_pool, cron_task_id)
            if err:
                raise Exception(err)

            crons, err = scheduler_utils.get_cron_tasks(cron_task_id)
            if err:
                raise Exception(err)
            description += ' Scheduled for %s' % crons[0]['schedule_description']

            audit.audit("create_remote_replication", description, request.META)

            return django.http.HttpResponseRedirect('/view_remote_replications?ack=created')
    except Exception as e:
        return_dict['base_template'] = "snapshot_replication_base.html"
        return_dict["page_title"] = 'Configure ZFS replication'
        return_dict['tab'] = 'view_remote_replications_tab'
        return_dict["error"] = 'Error configuring ZFS replication'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_remote_replication(request):
    return_dict = {}
    try:

        if 'remote_replication_id' not in request.REQUEST:
            raise Exception('Invalid request. Please use the menus.')
        remote_replication_id = request.REQUEST['remote_replication_id']
        replications, err = remote_replication.get_remote_replications(
            remote_replication_id)
        if err:
            raise Exception(err)
        if not replications:
            raise Exception('Specified replication definition not found')

        if request.method == "GET":
            return_dict['replication'] = replications[0]
            return django.shortcuts.render_to_response('update_remote_replication.html', return_dict, context_instance=django.template.context.RequestContext(request))
        elif request.method == "POST":
            if 'scheduler' not in request.POST:
                raise Exception("Incomplete request.")
            scheduler = request.POST.get('scheduler')
            schedule = scheduler.split()

            replication = replications[0]

            description = 'Replication of %s to pool %s on machine %s' % (
                replication['source_dataset'], replication['destination_pool'], replication['destination_ip'])

            py_scripts_path, err = common.get_python_scripts_path()
            if err:
                raise Exception(err)

            cmd = '%s/add_remote_replication_task.py %s %s %s %s' % (
                py_scripts_path, replications[0]['source_dataset'], replications[0]['destination_ip'], replications[0]['destination_user_name'], replications[0]['destination_pool'])
            # print cmd
            new_cron_task_id, err = scheduler_utils.add_cron_task(
                cmd, description, schedule[0], schedule[1], schedule[2], schedule[3], schedule[4])
            if err:
                raise Exception(err)
            ret, err = remote_replication.update_remote_replication(
                replications[0]['remote_replication_id'], new_cron_task_id)
            if err:
                raise Exception(err)

            cron_remove, err = scheduler_utils.delete_cron(
                int(replication['cron_task_id']))
            if err:
                raise Exception(err)
            crons, err = scheduler_utils.get_cron_tasks(new_cron_task_id)
            if err:
                raise Exception(err)
            description += ' Scheduled for %s' % crons[0]['schedule_description']

            audit.audit("modify_remote_replication", description, request.META)
            return django.http.HttpResponseRedirect('/view_remote_replications?ack=updated')
    except Exception as e:
        return_dict['base_template'] = "snapshot_replication_base.html"
        return_dict["page_title"] = 'Configure ZFS replication'
        return_dict['tab'] = 'view_remote_replications_tab'
        return_dict["error"] = 'Error configuring ZFS replication'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_remote_replication(request):
    return_dict = {}
    try:
        if 'remote_replication_id' not in request.REQUEST:
            raise Exception('Invalid request. Please use the menus.')
        remote_replication_id = request.REQUEST['remote_replication_id']
        return_dict['remote_replication_id'] = remote_replication_id
        replications, err = remote_replication.get_remote_replications(
            remote_replication_id)
        if err:
            raise Exception(err)
        if not replications:
            raise Exception(
                'Specified remote replication definition not found')

        if request.method == "GET":
            return_dict['replication'] = replications[0]
            return django.shortcuts.render_to_response("delete_zfs_replication_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:

            cron_remove, err = scheduler_utils.delete_cron(
                int(request.REQUEST['cron_task_id']))
            if err:
                raise Exception(err)

            ret, err = remote_replication.delete_remote_replication(
                remote_replication_id)
            if err:
                raise Exception(err)
            audit.audit("remove_remote_replication",
                        replications[0]['description'], request.META)
            return django.http.HttpResponseRedirect('/view_remote_replications?ack=cancelled')
    except Exception as e:
        return_dict['base_template'] = "snapshot_replication_base.html"
        return_dict["page_title"] = 'Cancel ZFS replication'
        return_dict['tab'] = 'view_remote_replications_tab'
        return_dict["error"] = 'Error cancelling ZFS replication'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
