import django
import django.template

from integral_view.forms import system_date_time_form
from integralstor_utils.date_time import update_date_time

def input_date_time(request):
    return_dict = {}
    try:
        form = system_date_time_form.date_time_form()
        return_dict['form'] = form
    except Exception, e:
        return_dict['base_template'] = "view_date_time.html"
        return_dict["page_title"] = 'Update system and hardware date and time'
        return_dict["error"] = 'Error viewing date time'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
    else:
        return django.shortcuts.render_to_response("view_date_time.html", return_dict, context_instance=django.template.context.RequestContext(request))

def update_system_date_time(request):
    return_dict = {}
    try:
        if request.method == 'POST':
            form = system_date_time_form.date_time_form(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                output, err = update_date_time(cd["system_date"], cd["system_time"])
                if err:
                    raise Exception(err)
                else:
                    if "date_set" in output and "time_set" in output:
                        print "datetime"
                        if output["date_set"] == True and output["time_set"] == True:
                            url = "/view_system_info?ack=datetime"
                    elif "time_set" in output:
                        print "time"
                        if output["time_set"] == True:
                            url="/view_system_info?ack=time"
                    elif "date_set" in output:
                        print "date"
                        if output["date_set"] == True:
                            url="/view_system_info?ack=date"
                    return django.http.HttpResponseRedirect(url)
            else:
                return_dict["form"] = form
                return django.shortcuts.render_to_response("view_date_time.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict["error"] = 'Error Performing Date Time Update'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html",  context_instance=django.template.context.RequestContext(request))
    else:
        return django.http.HttpResponseRedirect("/view_system_info")
