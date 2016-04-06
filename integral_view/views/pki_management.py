import django, django.template

from integralstor_common import audit, common, command, pki
import os, shutil

from integral_view.forms import pki_forms

def view_ssl_certificates(request):
  return_dict = {}
  try:
    cert_list, err = pki.get_ssl_certificates()
    if err:
      raise Exception(err)
  
    if "ack" in request.GET:
      if request.GET["ack"] == "deleted":
        return_dict['ack_message'] = "The certificate has been successfully deleted"
      elif request.GET["ack"] == "created_self_signed_cert":
        return_dict['ack_message'] = "A self signed SSL certificate has been successfully created"
      elif request.GET["ack"] == "uploaded_cert":
        return_dict['ack_message'] = "A new SSL certificate has been successfully uploaded"
    return_dict["cert_list"] = cert_list
    return django.shortcuts.render_to_response('view_ssl_certificates.html', return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "system_base.html"
    return_dict["page_title"] = 'SSL certificates'
    return_dict['tab'] = 'certificates_tab'
    return_dict["error"] = 'Error loading SSL certificates'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_ssl_certificate(request):

  return_dict = {}
  try:
    if 'name' not in request.REQUEST:
      raise Exception("No certificate name specified. Please use the menus")
    name = request.REQUEST["name"]
    return_dict["name"] = name

    if request.method == "GET":
      #Return the conf page
      return django.shortcuts.render_to_response("delete_ssl_certificate_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:

      ret, err = pki.delete_ssl_certificate(name)
      if err:
        raise Exception(err)
 
      audit_str = "Deleted SSL certificate name '%s'"%name
      audit.audit("delete_certificate", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_ssl_certificates?ack=deleted')
  except Exception, e:
    return_dict['base_template'] = "system_base.html"
    return_dict["page_title"] = 'Delete a SSL certificate'
    return_dict['tab'] = 'certificates_tab'
    return_dict["error"] = 'Error deleting SSL certificate'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_self_signed_ssl_certificate(request):
  return_dict = {}
  try:
    if request.method == "GET":
      #Return the conf page
      form = pki_forms.CreateSelfSignedCertForm()
      return_dict['form'] = form
      return django.shortcuts.render_to_response("create_self_signed_ssl_certificate.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = pki_forms.CreateSelfSignedCertForm(request.POST)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("create_self_signed_ssl_certificate.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      ret, err = pki.generate_self_signed_ssl_certificate(cd)
      if err:
        raise Exception(err)
 
      audit_str = "Created a self signed SSL certificate named %s"%cd['name']
      audit.audit("create_self_signed_certificate", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_ssl_certificates?ack=created_self_signed_cert')
  except Exception, e:
    return_dict['base_template'] = "system_base.html"
    return_dict["page_title"] = 'Create a self signed SSL certificate'
    return_dict['tab'] = 'certificates_tab'
    return_dict["error"] = 'Error creating a self signed SSL certificate'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def upload_ssl_certificate(request):
  return_dict = {}
  try:
    if request.method == "GET":
      #Return the conf page
      form = pki_forms.UploadCertForm()
      return_dict['form'] = form
      return django.shortcuts.render_to_response("upload_ssl_certificate.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = pki_forms.UploadCertForm(request.POST)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("upload_ssl_certificate.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      #print cd
      ret, err = pki.upload_ssl_certificate(cd)
      if err:
        raise Exception(err)
 
      audit_str = "Uploaded a SSL certificate named %s"%cd['name']
      audit.audit("upload_certificate", audit_str, request.META["REMOTE_ADDR"])
      return django.http.HttpResponseRedirect('/view_ssl_certificates?ack=uploaded_cert')
  except Exception, e:
    return_dict['base_template'] = "system_base.html"
    return_dict["page_title"] = 'Upload a SSL certificate'
    return_dict['tab'] = 'certificates_tab'
    return_dict["error"] = 'Error uploading a SSL certificate'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def upload_ssh_user_key(request):
  return_dict = {}
  if request.method == 'POST':
    try:
      authorized_key = request.FILES.get('pub_key')
      with open('/root/.ssh/authorized_keys', 'wb+') as destination:
          for chunk in authorized_key.chunks():
              destination.write(chunk)
      perm,err = pki.ssh_dir_permissions()
      if err:
        raise Exception(err)
      return_dict['ack_message'] = "Public key successfully added"
      return django.shortcuts.render_to_response("upload_ssh_user_key.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception,e:
      return_dict['base_template'] = "key_management_base.html"
      return_dict["page_title"] = 'Upload a Public Key'
      return_dict['tab'] = 'upload_public_key_tab'
      return_dict["error"] = 'Error adding Public key. Please check the value'
      return_dict["error_details"] = str(e)
      return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
    
  elif request.method == 'GET':
    return django.shortcuts.render_to_response("upload_ssh_user_key.html", return_dict, context_instance=django.template.context.RequestContext(request))

def upload_ssh_host_key(request):
  return_dict = {}
  hosts_file = "/root/.ssh/known_hosts"
  if request.method == 'POST':
    try:
      authorized_key = request.FILES.get('pub_key')
      ip = request.POST.get('ip')
      with open(hosts_file, 'wb+') as destination:
          for chunk in authorized_key.chunks():
              destination.write(chunk)
      #perm,err = pki.ssh_dir_permissions()
      with open(hosts_file,'r') as key:
        data = key.read()
      with open(hosts_file,'wb+') as key:
        key.write(ip+" "+data)
      return_dict["ack_message"] = "Successfully added host key"
      return django.shortcuts.render_to_response("upload_ssh_host_key.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception,e:
      return_dict['base_template'] = "key_management_base.html"
      return_dict["page_title"] = 'Upload a Host Key'
      return_dict['tab'] = 'upload_host_key_tab'
      return_dict["error"] = 'Error adding host key. Please check the value'
      return_dict["error_details"] = str(e)
      return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
        
  elif request.method == 'GET':
    return django.shortcuts.render_to_response("upload_ssh_host_key.html", return_dict, context_instance=django.template.context.RequestContext(request))

def edit_ssh_key(request):
  pass

def list_ssh_keys(request):
  pass

def delete_ssh_keys(request):
  pass

def download_ssh_keys(request):
  return_dict = {}
  try:
    # This gets the ssh file for download.
    key,err = pki.get_ssh_key() 
    # If the response is True instead of a file, the file does not exist. So generate it.
    if not key:
      status,err = pki.generate_ssh_key()
      if err:
        raise Exception(err)
    ssh_key,err = pki.get_ssh_key()
    if err:
      raise Exception(err)
    return_dict['ssh_key'] = ssh_key
    host_key,err = pki.get_ssh_host_identity_key()
    if err:
      raise Exception(err)
    return_dict['host_key'] = host_key
    return django.shortcuts.render_to_response("download_ssh_keys.html", return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception,e:
    return_dict['base_template'] = "key_management_base.html"
    return_dict["page_title"] = 'My Keys'
    return_dict['tab'] = 'my_public_key_tab'
    return_dict["error"] = 'Error fetching public keys'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

"""
## Not used now. But need to review this functionality and add a way to regenerate keys when it comes to security issues.
def regenerate_ssh_key(request):
  return_dict = {}
  key = pki.generate_new_ssh_key() 
  return_dict['my_ssh_key'] = key
  return django.shortcuts.render_to_response("show_my_ssh_key.html", return_dict, context_instance=django.template.context.RequestContext(request))
"""
