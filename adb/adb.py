from enum import IntEnum
import subprocess
from typing import List, Optional, Tuple
from PIL import Image
from io import BytesIO
import re
import time


EXECUTABLE_PATH = 'D:/Program Files/LDPlayer4.0/adb.exe'
COORDINATE_T = Tuple[int, int]


def adb_execute(cmd: str, device: str = '', stdout=None) -> Optional[subprocess.Popen]:
    if not device:
        header = EXECUTABLE_PATH
    else:
        header = EXECUTABLE_PATH + f' -s {device}'
    proc = subprocess.Popen(f'{header} {cmd}', stdout=stdout)
    if stdout == None:  # need not check output
        proc.wait()     # wait for process to finish
        # or else will cause trouble
        return None
    return proc


# on init
adb_execute('kill-server')
adb_execute('start-server')


class Key(IntEnum):
    HOME = 3
    BACK = 4
    VOLUME_INC = 24
    VOLUME_DEC = 25
    POWER = 26
    MUTE = 164


class AdbInterface:
    def __init__(self) -> None:
        self.device: str = None
        self.cache_ttl: int = 0
        self.cache_timing: float = 0
        self.cached_screen: Image.Image = None

    @staticmethod
    def get_devices() -> List[str]:
        devices = []
        proc = adb_execute('devices', stdout=subprocess.PIPE)
        try:
            stdout, stderr = proc.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            return []
        data = str(stdout, encoding='ascii')
        for line in data.splitlines():
            match = re.fullmatch(r'(.+?)[\t ](?:device)', line.strip())
            if match:
                devices.append(match.group(1))
        return devices

    @staticmethod
    def get(device: str, ttl: int = 10):
        device_list = AdbInterface.get_devices()
        if device not in device_list:
            raise RuntimeError(f'[{device}] not found')
        adb = AdbInterface()
        adb.device = device
        adb.cache_ttl = ttl
        return adb

    def text(self, string: str) -> None:
        adb_execute(f'shell input text "{string}"', device=self.device)

    def tap(self, position: COORDINATE_T) -> None:
        adb_execute(
            f'shell input tap {position[0]} {position[1]}', device=self.device)

    def swipe(self, src: COORDINATE_T, dst: COORDINATE_T, duration: int) -> None:
        # duration: in milliseconds
        adb_execute(
            f'shell input swipe {src[0]} {src[1]} {dst[0]} {dst[1]} {duration}', device=self.device)

    def keyevent(self, key: Key) -> None:
        adb_execute(f'shell input keyevent {key.value}', device=self.device)

    def screencap(self, cached: bool = True) -> Image.Image:
        if cached and \
                self.cached_screen != None and \
                time.time() - self.cache_timing < self.cache_ttl:
            return self.cached_screen

        proc = adb_execute(f'shell screencap -p',
                           stdout=subprocess.PIPE, device=self.device)
        data = proc.stdout.read()
        data = data.replace(b'\r\n', b'\n')
        try:
            img = Image.open(BytesIO(data))
        except:
            return None
        self.cached_screen = img
        self.cache_timing = time.time()
        return img


if __name__ == "__main__":
    adb = AdbInterface.get('emulator-5554')
    adb.keyevent(Key.VOLUME_INC)
    adb.keyevent(Key.VOLUME_DEC)
    adb.keyevent(Key.MUTE)
    adb.screencap().show()
