import django
import django.template

from integral_view.forms import system_date_time_forms
from integralstor_utils import system_date_time 

def update_system_date_time(request):
    return_dict = {}
    try:
        if request.method == 'GET':
            form = system_date_time_forms.DateTimeForm()
            return_dict['form'] = form
            return django.shortcuts.render_to_response("update_system_date_time.html", return_dict, context_instance=django.template.context.RequestContext(request))

        if request.method == 'POST':
            form = system_date_time_forms.DateTimeForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                output, err = system_date_time.update_date_time(cd["system_date"], cd["system_time"])
                if err:
                    raise Exception(err)
                else:
                    if "date_set" in output and "time_set" in output:
                        if output["date_set"] == True and output["time_set"] == True:
                            url = "/view_system_info?ack=system_datetime_set"
                    elif "time_set" in output:
                        if output["time_set"] == True:
                            url="/view_system_info?ack=system_time_set"
                    elif "date_set" in output:
                        if output["date_set"] == True:
                            url="/view_system_info?ack=system_date_set"
                    return django.http.HttpResponseRedirect(url)
            else:
                return_dict["form"] = form
                return django.shortcuts.render_to_response("update_system_date_time.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict["base_template"] = 'system_base.html'
        return_dict['page_title'] = 'Update system and hardware date and time'
        return_dict["error"] = 'Error Performing Date Time Update'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
    else:
        return django.http.HttpResponseRedirect("/view_system_info")
