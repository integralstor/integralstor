#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "integral_view.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
