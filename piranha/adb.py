import logging
import subprocess
from datetime import datetime

from utils import *


class ADB:
    def __init__(self, adb_bin):
        self.adb_bin = adb_bin

    def connect(self, ip = ''):
        cmd = '%s connect %s' % (self.adb_bin, ip)
        return os_run(cmd) == 0

    def get_id(self):
        cmd = '%s devices -l | grep "device usb" | head -n1 | awk \'{print $1 }\'' % (self.adb_bin)
        try:
            output = subprocess.check_output(cmd, shell = True, universal_newlines = True)
        except:
            logging.error('Unable to get smartphone ID')
            return None
        return output.strip()

    def install(self, apk):
        cmd = '%s install %s' % (self.adb_bin, apk)
        return os_run(cmd) == 0

    def grant(self, handle, permission):
        cmd = '%s shell pm grant %s %s' % (self.adb_bin, handle, permission)
        return os_run(cmd) == 0

    def run(self, handle):
        cmd = '%s shell monkey -p %s 25' % (self.adb_bin, handle)
        return os_run(cmd) == 0

    def set_date_time(self):
        d = datetime.now()
        cmd = '%s shell  \'su -c "date -u %s" ; su -c "am broadcast -a android.intent.action.TIME_SET"\'  ' % (
        self.adb_bin, d.strftime('%m%d%H%M'))
        return os_run(cmd) == 0

    def get_props(self):
        cmd = '%s shell getprop | tr \'[\' \'"\' | tr \']\' \'"\'' % self.adb_bin
        try:
            output = subprocess.check_output(cmd, shell = True, universal_newlines = True)
        except:
            logging.error('Unable to get smartphone properties')
            return None
        return output

    def get_property(self, property):
        cmd = '%s shell getprop %s' % (self.adb_bin, property)
        try:
            output = subprocess.check_output(cmd, shell = True, universal_newlines = True)
        except:
            logging.error('Unable to get smartphone properties')
            return None
        return output.strip()

    def disconnect(self, ip):
        cmd = '%s disconnect %s' % (self.adb_bin, ip)
        return os_run(cmd) == 0
