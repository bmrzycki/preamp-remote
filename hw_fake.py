import random
import time

class Range(object):
    def __init__(self, a, kind='wrap'):
        self.a = a
        self.kind = kind
        self.idx = 0
        self.max = len(a) - 1

    def val(self):
        return str(self.a[self.idx])

    def inc(self):
        if self.idx + 1 > self.max:
            if self.kind == 'wrap':
                self.idx = 0
        else:
            self.idx += 1
        return self.val()

    def dec(self):
        if self.idx - 1 < 0:
            if self.kind == 'wrap':
                self.idx = self.max
        else:
            self.idx -= 1
        return self.val()

    def set(self, val):
        val = str(val)
        for i in range(self.max+1):
            if str(self.a[i]) == val:
                self.idx = i
                return


_mode_map = { 193: 0,
              194: 1,
              195: 2,
              196: 3,
              197: 4,
              198: 5,
              199: 6,
              200: 7,
              201: 8,
              202: 9,
              203: 11,
              204: 12,
              205: 13,
              206: 14,
              207: 15,
              208: 16,
              209: 17,
              210: 17,
              211: 10 }


class Preamp(object):
    def __init__(self, port):
        self.port = port
        # Valid volume levels are off, or -99.0 to 14.0 in steps of 0.5.
        self.vol = Range(
            ['off'] + list(map(lambda x: x/10.0, range(-990, 145, 5))),
            kind='saturate')
        self.mute = Range(['off', 'on'])
        self.input = Range(list(range(1, 20+1)))
        self.mode = Range(list(range(0, 18+1)))

    def _input_name(self, val):
        if val == '1':
            return 'TV'
        if val == '2':
            return 'Bluetooth'
        if val == '3':
            return 'HTPC'
        return f"input {val}"

    def _rsp(self, cmd):
        # NOTE: we act as if STAT OFF is always enabled.
        cmd = cmd.lower()
        if cmd == 'stat main':
            inp = self.input.val()
            name = self._input_name(inp)
            vol = self.vol.val()
            if vol != 'off' and self.mute.val() == 'on':
                vol += " muted"
            return [ f"SY MAIN {inp} {name}",
                     f"SY VOLR {vol}" ]
        if cmd == 'stat mode':
            return [ f"SY MODE {self.mode.val()}" ]
        if cmd == 'stat audio':
            audio = random.randrange(0, 28 + 1)
            sr = random.choice([2, 3, 4, 5, 6, 7, 10])
            return [ f"SY AUDIO {audio} {sr}" ]
        if cmd == 'stat video':
            video = random.randrange(0, 18 + 1)
            return [ f"SY VIDEO {video}" ]
        if cmd == 'stat temp':
            c = random.randrange(30, 50+1)
            return [ f"SY TEMP {c}" ]
        if cmd == 'stat vers':
            return  [ 'SY VERS 3.1.0 build 0114' ]
        if cmd == 'stat ac':
            ac = random.randrange(118, 126 + 1)
            return [ f"SY AC {ac}" ]
        elif cmd in ('minp+', 'irc 10'):
            self.input.inc()
        elif cmd in ('minp-', 'irc 11'):
            self.input.dec()
        elif cmd in ('mvol+', 'irc 16'):
            self.vol.inc()
            self.mute.set('off')
        elif cmd in ('mvol-', 'irc 17'):
            self.vol.dec()
            self.mute.set('off')
        elif cmd.startswith('vola '):
            num = int(cmd.split()[1])
            if num == 0:
                self.vol.set('off')
            else:
                self.vol.set(num - 86.0)
                self.mute.set('off')
        elif cmd in ('mute', 'irc 152'):
            self.mute.set('on')
        elif cmd in ('unmt', 'irc 153'):
            self.mute.set('off')
        elif cmd == 'irc 13':
            self.mute.inc()
        elif cmd.startswith('irc '):
            num = int(cmd.split()[1])
            if num in range(2, 9+1):
                self.input.set(num-1)  # input 1-8
            elif num in range(120, 131+1):
                self.input.set(num-111)  # input 9-20
            elif num in range(193, 211+1):
                self.mode.set(_mode_map[num])  # mode 0-18
        return []

    def _wait(self, cmd):
        sp = cmd.split()
        time.sleep(int(sp[1]) / 1000.0)
        return []

    def cmd(self, cmd_list):
        a = []
        for c in cmd_list:
            if c.lower().startswith('wait '):
                a.append(self._wait(c))
            else:
                a.append(self._rsp(c))
        return a
