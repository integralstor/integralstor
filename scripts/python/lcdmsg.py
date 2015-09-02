#!/usr/bin/python

import sys, os
import subprocess
import re, logging

from integralstor_common import common

def process_call(command):
  try:
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output = ""
    while True:
        out = process.stdout.readline()
        if out == '' and process.poll() != None: break
        output += out
  except Exception, e:
    return None, 'Error executing command : %s'%str(e)
  else:
    return (process.returncode, output), None


if __name__ == "__main__":
  try:
    lcd = []
    bin_dir, err = common.get_bin_dir()
    if err:
      raise Exception(err)
    fpctl = '%s/fpctl'%bin_dir
    lcd.append(fpctl)
    lcd.append("clear")
    (ret, output), err = process_call(lcd)
    if err:
      raise Exception(err)
  
    lcd = []
    args = len(sys.argv)
    if args == 2:
      lcd.append(fpctl)
      lcd.append("print")
      lcd.append(sys.argv[1])
      (ret, output), err = process_call(lcd)
      if err:
        raise Exception(err)
    elif args == 3:
      lcd.append(fpctl)
      lcd.append("move")
      lcd.append("0")
      lcd.append("0")
      (ret, output), err = process_call(lcd)
      if err:
        raise Exception(err)
      lcd = []
      lcd.append(fpctl)
      lcd.append("print")
      lcd.append(sys.argv[1])
      (ret, output), err = process_call(lcd)
      if err:
        raise Exception(err)
      lcd = []
      lcd.append(fpctl)
      lcd.append("move")
      lcd.append("0")
      lcd.append("1")
      (ret, output), err = process_call(lcd)
      if err:
        raise Exception(err)
      lcd = []
      lcd.append(fpctl)
      lcd.append("print")
      lcd.append(sys.argv[2])
      (ret, output), err = process_call(lcd)
      if err:
        raise Exception(err)
    else:
      lcd.append(fpctl)
      lcd.append("print")
      lcd.append('integral-stor')
      (ret, output), err = process_call(lcd)
      if err:
        raise Exception(err)
  
  except Exception, e:
    print 'Error displaying on LCD : %s'%str(e)
    sys.exit(-1)
  else:
    sys.exit(0)

