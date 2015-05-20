#Integral View's internal logging module that is an extention to the python/django loggin module

import fractalio
from fractalio import db, common

db_path = common.get_db_path()

import logging
logger = logging.getLogger(__name__)

def set_log_level(level):
  if level not in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]:
    logger.setLevel(logging.INFO)
  else:
    d1 = db.read_single_row("%s/integral_view_config.db"%db_path, "select * from global_params")
    cmd_list = []
    if d1:
      cmd = ["update global_params set logging_level=? where id = ?", (level, 1,)]
    else:
      cmd = ["insert into global_params (logging_level, id) values(?,?)", (level, 1,)]
    cmd_list.append(cmd)
    db.execute_iud("%s/integral_view_config.db"%db_path, cmd_list)
    logger.setLevel(level)

def get_log_level_str():
  level = get_log_level()
  if level == logging.DEBUG:
    return 'Debug'
  elif level == logging.WARNING:
    return 'Warnings'
  elif level == logging.INFO:
    return 'Information'
  elif level == logging.ERROR:
    return 'Errors'
  else:
    return 'Unknown'

def get_log_level():
  d = None
  conn = None
  try :
    d = db.read_single_row("%s/integral_view_config.db"%db_path, "select * from global_params where id=1")
    if d  and "logging_level" in d:
      return d["logging_level"]
    else:
      #Not yet set so insert the default and return it
      cmd_list = []
      cmd = ["insert into global_params (logging_level, id) values(?,?)", (logging.INFO, 1,)]
      cmd_list.append(cmd)
      db.execute_iud("%s/integral_view_config.db"%db_path, cmd_list)
      return logging.INFO
  except Exception, e:
    print "Error inserting log level : %s"%str(e)

def info(msg):
  logger.setLevel(get_log_level())
  logger.info(msg)

def debug(msg):
  logger.setLevel(get_log_level())
  logger.debug(msg)

def critical(msg):
  logger.setLevel(get_log_level(logger))
  logger.critical(msg)

def warn(msg):
  logger.setLevel(get_log_level(logger))
  logger.warn(msg)

def error(msg):
  logger.setLevel(get_log_level(logger))
  logger.error(msg)
