from adb import AdbInterface
from utils.interface import Interface

try:
    adb = AdbInterface.get('emulator-5554')
except:
    adb = AdbInterface.get('127.0.0.1:5555')

ark_intf = Interface(adb, work_dir='ark/resource')
