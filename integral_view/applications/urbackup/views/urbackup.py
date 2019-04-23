import django
import django.template
from django.contrib.auth.decorators import login_required

from integralstor import networking

@login_required
def view_backup(request):
    return_dict = {}
    try:
        host = request.META['HTTP_HOST']
        if ':' in host:
            col_pos = host.find(':')
            if col_pos:
                host = host[:col_pos]
        url = '%s:55414' % host
        ret, err =  networking.check_url('http://%s'%url)
        if not ret:
            return_dict['url_access_error'] = err
        return_dict['url'] = url
        return django.shortcuts.render_to_response("view_backup.html", return_dict, context_instance=django.template.context.RequestContext(request))

    except Exception, e:
        return_dict['base_template'] = "urbackup_base.html"
        return_dict["page_title"] = 'Data backup'
        return_dict['tab'] = 'view_backup_tab'
        return_dict["error"] = 'Error loading backup URL'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

