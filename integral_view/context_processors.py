
from integralstor import config
import os.path
import json


def get_version(request):
    version = None
    try:
        version, err = config.get_version()
        if err:
            raise Exception('Error retrieving version number')
    except Exception, e:
        return {'version': 'Unspecified version'}
    else:
        return {'version': version}

def get_brand_config(request):
    return_dict = None
    try:
        return_dict, err = config.get_branding_config()
        if err:
            raise Exception(err)
    except Exception, e:
        print e
        return return_dict
    else:
        return return_dict


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
