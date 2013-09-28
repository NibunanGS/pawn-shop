#!/usr/bin/env python
from django.core.management import execute_manager
import imp
import sys

try:
    imp.find_module('settings') # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)


# Comment out, if you don't want debugging...
sys.path.append(r'/Applications/eclipse/plugins/org.python.pydev_2.8.1.2013072611/pysrc')

import pydevd
pydevd.patch_django_autoreload(patch_remote_debugger=True, patch_show_console=False)
# -- Debugging setting ends...


import settings
if __name__ == "__main__":
    execute_manager(settings)
