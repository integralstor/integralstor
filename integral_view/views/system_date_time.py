import django
import django.template

from integral_view.forms import date_time_form
from integralstor.update_system_date_time import update_system_date_time


def view_date_time(request):
    return_dict = {}
    try:
        if request.method == 'GET':
            if 'err' in request.GET:
                return_dict["err"] = True
            form = date_time_form.date_time_form()
            return_dict['form'] = form
    except Exception, e:
        return_dict['base_template'] = "view_date_time.html"
        return_dict["page_title"] = 'Update System and Hardware Date and Time'
        return_dict["error"] = 'Error viewing date time'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
    else:
        return django.shortcuts.render_to_response("view_date_time.html", return_dict, context_instance=django.template.context.RequestContext(request))

def update_date_time(request):
    try:
        if request.method == 'POST':
            date = request.POST["date"]
            time = request.POST["time"]
            if date == "":
                date = None
            if time == "":
                time = None
            if (date==None and time==None):
                return django.http.HttpResponseRedirect("/view_date_time?err=empty")
            output, err = update_system_date_time(date, time)
            if err:
                raise Exception(err)
    except Exception, e:
        return_dict["error"] = 'Error Performing Date Time Update'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
    else:
        return django.http.HttpResponseRedirect("/view_system_info")
