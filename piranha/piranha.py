from core import *
from adb import *

adb = ADB('/home/lambda/Android/Sdk/platform-tools/adb')
p = PiRanha('http://localhost:8000', 'dsfs')
p.register_smartphone(adb, 'Asus')