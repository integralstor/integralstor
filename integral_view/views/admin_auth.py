import django
import django.template
from django.contrib import auth
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required

import os

import integral_view
from integral_view.forms import admin_forms
from integral_view.utils import iv_logging
from integralstor import audit, django_utils, command


def login(request):
    """ Used to login a user into the management utility"""
    try:
        return_dict = {}
        authSucceeded = False

        if request.method == 'POST':
            iv_logging.info("Login request posted")
            # Someone is submitting info so check it
            form = admin_forms.LoginForm(request.POST)
            if form.is_valid():
                # submitted form is valid so now try to authenticate
                # if not valid then fall out to end of function and return form to user
                # with existing data
                cd = form.cleaned_data
                username = cd['username']
                password = cd['password']
                # Try to authenticate
                user = django.contrib.auth.authenticate(
                    username=username, password=password)
                if user is not None and user.is_active:
                    '''
                    #Uncomment if we want to kick out an already logged in user.
                    # Clear the session if the user has been logged in anywhere else.
                    sessions = Session.objects.all()
                    for s in sessions:
                      if s.get_decoded() and (int(s.get_decoded()['_auth_user_id']) == user.id):
                        s.delete()
                    '''
                    # authentication succeeded! Login and send to home screen
                    django.contrib.auth.login(request, user)
                    iv_logging.info(
                        "Login request from user '%s' succeeded" % username)
                    authSucceeded = True
                else:
                    iv_logging.info(
                        "Login request from user '%s' failed" % username)
                    return_dict['invalidUser'] = True
            else:
                # Invalid form
                iv_logging.debug("Invalid login information posted")
        else:
            # GET request so create a new form and send back to user
            form = admin_forms.LoginForm()
            # Clear the session if the user has been logged in anywhere else.
            sessions = Session.objects.all()
            for s in sessions:
                if s.get_decoded() is not None and s.get_decoded().get('_auth_user_id') is not None:
                    return_dict['session_active'] = True

        return_dict['form'] = form

        if authSucceeded:
            return django.http.HttpResponseRedirect('/monitoring/view_dashboard/sys_health')

        # For all other cases, return to login screen with return_dict
        # appropriately populated
        return django.shortcuts.render_to_response('login_form.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        s = str(e)
        return_dict["error"] = "An error occurred when processing your request : %s" % s
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))


def logout(request):
    """ Used to logout a user into the management utility"""
    try:
        iv_logging.info("User '%s' logged out" % request.user)
        # Clear the session if the user has been logged in anywhere else.
        sessions = Session.objects.all()
        for s in sessions:
            if (s.get_decoded() and int(s.get_decoded()['_auth_user_id']) == request.user.id) or not s.get_decoded():
                print 'deleting!'
                s.delete()
        django.contrib.auth.logout(request)
        return django.http.HttpResponseRedirect('/login/')
    except Exception, e:
        return_dict['base_template'] = "dashboard_base.html"
        return_dict["page_title"] = 'Logout'
        return_dict['tab'] = 'disks_tab'
        return_dict["error"] = 'Error logging out'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))


def update_admin_password(request):
    """ Used to change a user's password for the management utility"""

    try:
        return_dict = {}

        if request.user and request.user.is_authenticated():
            if request.method == 'POST':
                iv_logging.debug("Admin password change posted")
                # user has submitted the password info
                form = admin_forms.ChangeAdminPasswordForm(request.POST)
                if form.is_valid():
                    cd = form.cleaned_data
                    oldPasswd = cd['oldPasswd']
                    newPasswd1 = cd['newPasswd1']
                    newPasswd2 = cd['newPasswd2']
                    # Checking for old password is done in the form itself
                    if request.user.check_password(oldPasswd):
                        if newPasswd1 == newPasswd2:
                            # all systems go so now change password
                            request.user.set_password(newPasswd1)
                            request.user.save()
                            return_dict['ack_message'] = 'Password changed sucessful.'
                            iv_logging.info(
                                "Admin password change request successful.")
                            audit_str = "Changed admin password"
                            audit.audit("modify_admin_password",
                                        audit_str, request)
                        else:
                            return_dict['error'] = 'New passwords do not match'
                # else invalid form or error so existing form data to return_dict and
                # fall through to redisplay the form
                if 'success' not in return_dict:
                    return_dict['form'] = form
                    iv_logging.info("Admin password change request failed.")
            else:
                form = admin_forms.ChangeAdminPasswordForm()
                return_dict['form'] = form

            return django.shortcuts.render_to_response('update_admin_password_form.html', return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            # User not authenticated so return a login screen
            return django.http.HttpResponseRedirect('/login/')
    except Exception, e:
        return_dict['base_template'] = "system_base.html"
        return_dict["page_title"] = 'Change admininistrator password'
        return_dict['tab'] = 'system_info_tab'
        return_dict["error"] = 'Error changing administrator password'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))




def admin_login_required(view):

    def new_view(request, *args, **kwargs):
        if request.user.username == 'superadmin':
            return view(request, *args, **kwargs)
        else:
            return django.http.HttpResponseRedirect('/login')

    return new_view


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
