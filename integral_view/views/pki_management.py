import django, django.template

from integralstor_common import audit, common, command, certificates
import os, shutil

from integral_view.forms import pki_forms

#import json, time, os, shutil, tempfile, os.path, re, subprocess, sys, shutil, pwd, grp, stat,datetime

def view_certificates(request):
  return_dict = {}
  try:
    cert_list, err = certificates.get_certificates()
    if err:
      raise Exception(err)
  
    conf = None
    if "action" in request.GET:
      if request.GET["action"] == "deleted":
        conf = "The certificate has been successfully deleted"
      elif request.GET["action"] == "created_self_signed_cert":
        conf = "A self signed SSL certificate has been successfully created"
      elif request.GET["action"] == "uploaded_cert":
        conf = "A new SSL certificate has been successfully uploaded"
      if conf:
        return_dict["conf"] = conf
    return_dict["cert_list"] = cert_list
    return django.shortcuts.render_to_response('view_certificates.html', return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "system_base.html"
    return_dict["page_title"] = 'SSL certificates'
    return_dict['tab'] = 'certificates_tab'
    return_dict["error"] = 'Error loading SSL certificates'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_certificate(request):

  return_dict = {}
  try:
    if 'name' not in request.REQUEST:
      raise Exception("No certificate name specified. Please use the menus")
    name = request.REQUEST["name"]
    return_dict["name"] = name

    if request.method == "GET":
      #Return the conf page
      return django.shortcuts.render_to_response("delete_certificate_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:

      ret, err = certificates.delete_certificate(name)
      if err:
        raise Exception(err)
 
      audit_str = "Deleted SSL certificate name '%s'"%name
      audit.audit("delete_certificate", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_certificates?action=deleted')
  except Exception, e:
    return_dict['base_template'] = "system_base.html"
    return_dict["page_title"] = 'Delete a SSL certificate'
    return_dict['tab'] = 'certificates_tab'
    return_dict["error"] = 'Error deleting SSL certificate'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_self_signed_cert(request):
  return_dict = {}
  try:
    if request.method == "GET":
      #Return the conf page
      form = pki_forms.CreateSelfSignedCertForm()
      return_dict['form'] = form
      return django.shortcuts.render_to_response("create_self_signed_cert.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = pki_forms.CreateSelfSignedCertForm(request.POST)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("create_self_signed_cert.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      ret, err = certificates.generate_self_signed_certificate(cd)
      if err:
        raise Exception(err)
 
      audit_str = "Created a self signed SSL certificate named %s"%cd['name']
      audit.audit("create_self_signed_certificate", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_certificates?action=created_self_signed_cert')
  except Exception, e:
    return_dict['base_template'] = "system_base.html"
    return_dict["page_title"] = 'Create a self signed SSL certificate'
    return_dict['tab'] = 'certificates_tab'
    return_dict["error"] = 'Error creating a self signed SSL certificate'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def upload_cert(request):
  return_dict = {}
  try:
    if request.method == "GET":
      #Return the conf page
      form = pki_forms.UploadCertForm()
      return_dict['form'] = form
      return django.shortcuts.render_to_response("upload_cert.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = pki_forms.UploadCertForm(request.POST)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("upload_cert.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      #print cd
      ret, err = certificates.upload_certificate(cd)
      if err:
        raise Exception(err)
 
      audit_str = "Uploaded a SSL certificate named %s"%cd['name']
      audit.audit("upload_certificate", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_certificates?action=uploaded_cert')
  except Exception, e:
    return_dict['base_template'] = "system_base.html"
    return_dict["page_title"] = 'Upload a SSL certificate'
    return_dict['tab'] = 'certificates_tab'
    return_dict["error"] = 'Error uploading a SSL certificate'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
