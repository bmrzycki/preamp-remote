from time import sleep

import serial  # external pyserial 3.0+

class Preamp():
    def __init__(self, port):
        # The SSP-800 baud is normally 9600. To change to 115200 use the
        # service menu:
        #  1. With the SSP-800 powered on, press and release the MENU
        #     button on the front of the unit.
        #  2. On the remote control, press and release the button
        #     sequence in order: F1, F2, F3, F4.
        self._s = serial.Serial(
            port=port, baudrate=115200, bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
            xonxoff=False, rtscts=False, dsrdtr=False)
        self._count = { 'stat main'  : 2,
                        'stat mode'  : 1,
                        'stat audio' : 1,
                        'stat video' : 1,
                        'stat temp'  : 1,
                        'stat vers'  : 1,
                        'stat ac'    : 1 }
        self.cmd(["stat off"])

    def _write(self, data, timeout=0.2):
        _ = self._read(self._s.in_waiting, 0.0)  # Purge any buffered foo.
        self._s.write_timeout = timeout
        try:
            count = self._s.write(bytes(data + '\n', 'ascii'))
        except serial.SerialTimeoutException:
            count = 0
        if count:
            sleep(timeout)
        return count

    def _read(self, count=0, timeout=0.2, max_retries=3):
        self._s.timeout = timeout
        c = self._s.read(3).decode()
        if not c:
            return "ERR no response from preamp"
        if c == '?\r\n':
            return "ERR invalid request"
        if c != '!\r\n':
            return f"ERR unexpected response '{c}'"

        buf, retries = '', max_retries
        while count:
            c = self._s.read(1).decode()
            if c:
                retries = max_retries  # Got char, reset the retry count.
                if c == '\r':
                    continue
                if c == '\n':
                    count -= 1
                buf += c
            else:
                retries -= 1
                if retries < 1:
                    return f"ERR incomplete read '{buf}'"
                sleep(timeout)
        return buf

    def _wait(self, cmd):
        sp = cmd.split()
        sleep(int(sp[1]) / 1000.0)
        return []

    def cmd(self, cmd_list):
        a = []
        for cmd in cmd_list:
            rsp, cmd = [], cmd.strip()
            if cmd.lower().startswith('wait '):
                rsp = self._wait(cmd)
            elif cmd and self._write(cmd):
                raw = self._read(count=self._count.get(cmd.lower(), 0))
                raw = raw.rstrip()
                if raw:
                    rsp = raw.split('\n')
            a.append(rsp)
        return a
