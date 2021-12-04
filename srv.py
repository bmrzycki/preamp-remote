#!/usr/bin/env python3

import argparse

from collections import deque
from configparser import ConfigParser
from mimetypes import guess_type
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from json import dumps, loads
from sys import argv
from threading import Lock
from urllib.parse import urlparse

# local imports
from pa_ssp800 import request as pa_reqfn
from pa_ssp800 import response as pa_rspfn
from pa_ssp800 import commands as pa_commands

API_PATH = '/1'
VERBOSE = 0

_BASE = Path(__file__).parent.resolve()
_NET = {
    'name' : '',  # listen on any TCP device
    'port' : 8000,
}
_PREAMP = {
    'dev'      : 'fake',  # a fake preamp for testing
    'baudrate' : 9600,
}
_VERSION = {
    'rev'  : 'unknown',
    'date' : '',
}
_DATA = {
    '/cli.py' : { 'file' : str(_BASE.joinpath('cli.py')),
                  'type' : 'application/x-python-code' },
}
_DESC = {}

def _hostinfo():
    def uptime():
        value = 'unknown'
        p = Path('/proc/uptime')
        if p.is_file():
            def _value(s):
                d, s = divmod(s, 86400)
                h, s = divmod(s,  3600)
                m, s = divmod(s,    60)
                if d:
                    return f"{d}d{h:02d}h{m:02d}m{s:02d}s"
                if h:
                    return f"{h:02d}h{m:02d}m{s:02d}s"
                if m:
                    return f"{m:02d}m{s:02d}s"
                return f"{s:02d}s"
            with open(p) as f:
                s = round(float(f.readline().split()[0]))
                value = _value(s)
        return value

    def loadavg():
        value = 'unknown'
        p = Path('/proc/loadavg')
        if p.is_file():
            with open(p) as f:
                v = float(f.readline().split()[0]) * 100.0
                value = f"{v:.1f}%"
        return value

    def temp0():
        value = 'unknown'
        p = Path('/sys/class/thermal/thermal_zone0/temp')
        if p.is_file():
            with open(p) as f:
                v = float(f.readline().strip()) / 1000.0
                value = f"{v:.2f} c"
        return value

    return [ f"SY UPTIME {uptime()}",
             f"SY LOADAVG {loadavg()}",
             f"SY TEMP0 {temp0()}",
             f"SY TTY {_PREAMP['dev']} @ {_PREAMP['baudrate']}" ]


def setup_hw():
    if _PREAMP['dev'] == 'fake':
        from hw_fake import Preamp
    else:
        from hw_ssp800 import Preamp

    class HW():
        def __init__(self):
            self.p  = Preamp(_PREAMP['dev'], _PREAMP['baudrate'])
            self.lp = Lock()

        def submit(self, cmd_list):
            a = []
            self.lp.acquire()
            try:
                a = self.p.cmd(cmd_list)
            finally:
                self.lp.release()
            return a

    global _HW
    _HW = HW()


def setup_web_data():
    web_p = _BASE.joinpath('web')
    for p in web_p.rglob('*'):
        if p.is_file():
            url = str(p).partition(str(web_p))[2]
            _DATA[url] = { 'file' : str(p),
                           'type' : guess_type(p)[0] }
    _DATA['/'] = _DATA['/index.html']


def setup_desc():
    for n in pa_commands():
        _DESC[n['name']] = { 'desc' : n['desc'], 'p1' : n['p1'] }
    # Extend stat command with meta-commands handled in this server.
    _DESC['stat']['p1']['swvers'] = 'Request software version information.'
    _DESC['stat']['p1']['hostinfo'] = 'Request software host information.'


class DeviceCmd():
    def __init__(self, cmd, reqfn=None, rspfn=None):
        self.cmd = self.raw = cmd
        self.rsps = []
        self.raw_rsps = []
        def _nop(s):
            return True, s
        self.reqfn = self.rspfn = _nop
        if reqfn is not None:
            self.reqfn = reqfn
        if rspfn is not None:
            self.rspfn = rspfn
        self.ok, ret = self.reqfn(self.cmd)
        if self.ok:
            self.raw = ret
        else:
            self.rsps.append(ret)

    def responses(self, raw_rsps):
        self.raw_rsps = raw_rsps
        for r in raw_rsps:
            ok, rsp = self.rspfn(r)
            if self.ok and not ok:
                self.ok = False
            self.rsps.append(rsp)


class DeviceData():
    def __init__(self, subfn, reqfn=None, rspfn=None):
        self.subfn = subfn
        self.reqfn = reqfn
        self.rspfn = rspfn
        self.data = []

    def add(self, cmd):
        self.data.append(DeviceCmd(cmd, self.reqfn, self.rspfn))

    def submit(self):
        all_raws, next_i = [], deque()
        for i in range(len(self.data)):
            if self.data[i].ok:
                next_i.appendleft(i)
                all_raws.append(self.data[i].raw)
        # Only call subfn once with an array of raw requests.
        # The call may be expensive and is under a global lock.
        all_sub_rsps = self.subfn(all_raws)
        for raw_rsps in all_sub_rsps:
            self.data[next_i.pop()].responses(raw_rsps)


class Srv(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        if VERBOSE > 1:
            super().log_message(fmt, *args)

    def _rsp_json(self, data):
        raw = bytes(dumps(data), 'utf-8')
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-length', len(raw))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(raw)

    def _rsp_file(self, fname, content_type):
        self.send_response(200)
        if content_type is not None:
            self.send_header('Content-type', content_type)
        self.send_header('Content-length', Path(fname).stat().st_size)
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(open(fname, 'rb').read())

    def _reqs(self, reqs):
        if len(reqs) == 0:
            self.send_error(400, 'No requests received')
            return

        def _el(request, responses, req_raw=''):
            if not req_raw:
                req_raw = request
            return { 'request'   : request,
                     'responses' : responses,
                     'req_raw'   : req_raw }

        dd_pa = DeviceData(_HW.submit, reqfn=pa_reqfn, rspfn=pa_rspfn)
        rsps = []
        for r in reqs:
            r = str(r).lower()
            if r == 'stat swvers':
                v = f"{_VERSION['rev']}"
                if _VERSION['date']:
                    v += f" ({_VERSION['date']})"
                rsps.append(_el(r, [f"SY SWVERS {v}"]))
            elif r == 'stat hostinfo':
                rsps.append(_el(r, _hostinfo()))
            else:
                dd_pa.add(r)

        dd_pa.submit()
        for d in dd_pa.data:
            rsps.append(_el(d.cmd, d.rsps, req_raw=d.raw))
        self._rsp_json(rsps)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == '/commands':
            self._rsp_json(_DESC)
            return
        f = _DATA.get(u.path, None)
        if f is None:
            self.send_error(404)
            return
        self._rsp_file(f['file'], f['type'])

    def do_POST(self):
        if self.path != API_PATH:
            self.send_error(404)
            return
        clen = int(self.headers['Content-Length'])
        raw = self.rfile.read(clen).decode('utf-8')
        try:
            q = loads(raw)
        except Exception as e:
            self.send_error(400, f"Bad JSON ({e}): {raw}")
            return
        if not isinstance(q, list):
            self.send_error(400, f"JSON must be a list: {q}")
            return
        self._reqs(q)


def main(args_raw):
    global VERBOSE
    p = argparse.ArgumentParser(
        description='Preamp HTTP REST API front-end server',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument(
        '-c', '--config',
        type=argparse.FileType('r', encoding='utf-8'),
        default=str(_BASE.joinpath('default.cfg')), help='config file')
    p.add_argument(
        '-v', '--verbose',
        default=VERBOSE, action='count',
        help='verbosity, repeat to increase')
    args = p.parse_args(args_raw)
    VERBOSE = args.verbose

    cfg = ConfigParser()
    try:
        cfg.read_file(args.config)
    except Exception as e:
        p.error(str(e))

    _NET['name'] = cfg.get('net', 'name', fallback=_NET['name'])
    _NET['port'] = cfg.getint('net', 'port', fallback=_NET['port'])
    _PREAMP['dev'] = cfg.get('preamp', 'dev', fallback=_PREAMP['dev'])
    _PREAMP['baudrate'] = cfg.getint('preamp', 'baudrate',
                                     fallback=_PREAMP['baudrate'])
    _VERSION['rev'] = cfg.get('version', 'rev', fallback=_VERSION['rev'])
    _VERSION['date'] = cfg.get('version', 'date', fallback=_VERSION['date'])

    setup_web_data()
    setup_desc()
    setup_hw()

    if VERBOSE > 1:
        for d, n in ((_NET, 'net'), (_PREAMP, 'preamp'),
                     (_VERSION, 'version')):
            for k in sorted(d):
                print(f"{n}.{k} = {d[k]}")

    h = ThreadingHTTPServer((_NET['name'], _NET['port']), Srv)
    try:
        h.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        h.server_close()


if __name__ == "__main__":
    main(argv[1:])
