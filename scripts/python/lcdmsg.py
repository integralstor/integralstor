#!/usr/bin/python

import sys, os
import subprocess
import re, logging

from integralstor_common import common

def process_call(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output = ""
    while True:
        out = process.stdout.readline()
        if out == '' and process.poll() != None: break
        output += out
    return (process.returncode, output)

if __name__ == "__main__":
  lcd = []
  fpctl = '%s/fpctl'%common.get_bin_dir()
  lcd.append(fpctl)
  lcd.append("clear")
  (ret, output) = process_call(lcd)

  lcd = []
  args = len(sys.argv)
  if args == 2:
    lcd.append(fpctl)
    lcd.append("print")
    lcd.append(sys.argv[1])
    (ret, output) = process_call(lcd)
  elif args == 3:
    lcd.append(fpctl)
    lcd.append("move")
    lcd.append("0")
    lcd.append("0")
    (ret, output) = process_call(lcd)
    lcd = []
    lcd.append(fpctl)
    lcd.append("print")
    lcd.append(sys.argv[1])
    (ret, output) = process_call(lcd)
    lcd = []
    lcd.append(fpctl)
    lcd.append("move")
    lcd.append("0")
    lcd.append("1")
    (ret, output) = process_call(lcd)
    lcd = []
    lcd.append(fpctl)
    lcd.append("print")
    lcd.append(sys.argv[2])
    (ret, output) = process_call(lcd)
  else:
    lcd.append(fpctl)
    lcd.append("print")
    lcd.append('integral-stor')
    (ret, output) = process_call(lcd)

  sys.exit(0)
