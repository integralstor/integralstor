
from integralstor_common import common

def get_version(request):
  version = None
  try:
    version, err = common.get_version()
    if err:
      raise Exception('Error retrieving version number')
  except Exception, e:
    return {'version':'Unspecified version'}
  else:
    return {'version': version}
