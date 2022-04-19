#!/usr/bin/env python3

import argparse

from signal import signal, SIGPIPE, SIG_DFL
from sys import argv
from threading import Thread, Lock
from time import sleep

import evdev  # pip install --user evdev

from cli import Client, get_cfg  # local import

# Initial setup
#
# Hold button on bottom of dial for 5 seconds until light blinks.
#   root # bluetoothctl
#   [bluetoothctl] agent on
#   [bluetoothctl] default-agent
#
# Search for string "Surface Dial" to find its MAC.
#   [bluetoothctl] scan on
#
# Pair to the Surface Dial's MAC
#   [bluetoothctl] pair MAC
#
# (First time to double-check, Linux auto-pairs on reboots)
#   [bluetoothctl] connect SURFACE_MAC

VERBOSE = 0

class Volume():
    def __init__(self):
        self.clear()

    def clear(self):
        self._rel = 0
        self._count = 0
        self._mute = False
        self._reset = False

    def mute(self):
        self._mute = True

    def reset(self):
        self._reset = True

    def rel(self, v):
        if not self._mute and not self._reset:
            self._rel += v
            self._count += 1

    def data(self):
        return { 'rel'   : self._rel,
                 'count' : self._count,
                 'mute'  : self._mute,
                 'reset' : self._reset }

    def __repr__(self):
        return (f"Volume(rel={self._rel}, mute={self._mute}, "
                f"reset={self._reset})")


_VOL = Volume()
_VOL_LK = Lock()
_STOP = False


class Handler():
    def __init__(self, delay_long=0.4, dev_sleep=0.02):
        self._delay_long = delay_long
        self._dev_sleep = dev_sleep
        self._ts_btn = 0
        self._set_dev()

    def _set_dev(self):
        while True:
            for p in evdev.list_devices():
                try:
                    d = evdev.InputDevice(p)
                except:
                    continue
                if d.name == "Surface Dial System Multi Axis":
                    self.dev = d
                    return
            sleep(self._dev_sleep)

    def parse(self, event):
        global _VOL, _VOL_LK
        if (event.type == evdev.ecodes.EV_KEY and
            event.code == evdev.ecodes.BTN_0):
            if event.value == 1:  # Pressed
                self._ts_btn = event.timestamp()
            else:  # Released
                try:
                    _VOL_LK.acquire()
                    if (event.timestamp() - self._ts_btn) >= self._delay_long:
                        _VOL.reset()
                    else:
                        _VOL.mute()
                finally:
                    _VOL_LK.release()
                self._ts_btn = 0
            return

        if self._ts_btn:
            return  # Discard all dial rotations while pressed.

        if (event.type == evdev.ecodes.EV_REL and
            event.code == evdev.ecodes.REL_DIAL):
                try:
                    _VOL_LK.acquire()
                    _VOL.rel(event.value)
                finally:
                    _VOL_LK.release()
                return


def thread_http(cl):
    global _STOP, _VOL_LK, _VOL
    while not _STOP:
        try:
            _VOL_LK.acquire()
            d = _VOL.data()
            _VOL.clear()
        finally:
            _VOL_LK.release()

        cmd = []
        if d['reset']:
            cmd = ['vola 1']
        elif d['mute']:
            cmd = ['irc mute']
        elif d['rel'] and d['count']:
            vol = d['rel'] / float(d['count'])
            cmd = ['irc volume+']
            if vol < 0:
                cmd = ['irc volume-']
                vol = abs(vol)
            if vol > 7.0:
                cmd *= 3
            elif vol > 4.0:
                cmd *= 2
            elif vol > 2.0:
                pass  # x1 standard multiplier
            else:
                cmd = []
        if cmd:
            if VERBOSE > 2:
                print(f"cmd: {cmd}")
            try:
                ret = cl.fetch(cmd, timeout=0.2)
                if VERBOSE > 1:
                    print(f"response: {ret}")
            except Exception as e:
                if VERBOSE > 0:
                    print(f"fetch exception {e}")
            sleep(0.05)
        else:
            sleep(0.1)


def main(args_raw):
    global VERBOSE
    p = argparse.ArgumentParser(
        description='Surface Dial to volume daemon',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument(
        '-v', '--verbose',
        default=VERBOSE, action='count',
        help='verbosity, repeat to increase')
    args = p.parse_args(args_raw)
    VERBOSE = args.verbose

    cfg_d = get_cfg()
    cl = Client(cfg_d['name'], cfg_d['port'])
    h = Handler()
    t = Thread(target=thread_http, args=(cl,))
    t.start()

    while True:
        try:
            for event in h.dev.read_loop():
                h.parse(event)
        except KeyboardInterrupt:
            global _STOP
            _STOP = True
            t.join()
            return
        except OSError:
            # These OSErrors occur when the dial sleeps and Linux removes
            # the /dev/input/eventXX file. Re-establish a connection when
            # knob events wake it up again.
            h = Handler()


if __name__ == '__main__':
    signal(SIGPIPE, SIG_DFL)  # Suppress broken pipe exceptions.
    main(argv[1:])
