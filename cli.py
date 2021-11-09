#!/usr/bin/env python3

import argparse
import sys

from configparser import ConfigParser
from json import dumps, load
from pathlib import Path
from pprint import pformat
from signal import signal, SIGPIPE, SIG_DFL
from urllib.request import Request, urlopen

_DOTFILE = """
# -*- mode: Conf[Unix]; -*-
[server]
  name = {name}
  port = {port}
"""[1:]

class Client(object):
    def __init__(self, name, port):
        self.name = name
        self.port = port

    def fetch(self, cmd_list):
        u = Request(
            url=f'http://{self.name}:{self.port}/1',
            data=dumps(cmd_list).encode('utf-8'),
            headers={ 'Content-Type' : 'application/json' })
        try:
            fh = urlopen(u, timeout=5.0)
        except Exception as e:
            try:
                err = e.reason
            except:
                err = str(e)
            a = []
            for cmd in cmd_list:
                a.append({ 'request'   : cmd,
                           'responses' : [ f"ERR {err}" ] })
                return a
        return load(fh)

    def _commands(self):
        u = Request(
            url=f'http://{self.name}:{self.port}/commands')
        try:
            fh = urlopen(u, timeout=5.0)
        except Exception as e:
            try:
                err = e.reason
            except:
                err = str(e)
            return { '_err' : f"{err}" }
        return load(fh)

    def commands(self, prefix=''):
        raw = self._commands()
        if '_err' in raw:
            return raw
        d = { '_err' : '', '_pad' : 0 }
        for k in raw:
            d['_pad'] = max(d['_pad'], len(k))
            if k.startswith(prefix):
                d[k] = raw[k]
        return d


def desc_pretty(d, out_s):
    def _p1_sort(val):
        if isinstance(val, str) and val:
            tmp = val
            if tmp[0] in ('-', '+'):
                tmp = tmp[1:]
            if tmp.isdigit():
                return int(val)
        return val

    all_names = sorted(d.keys())
    for name in all_names:
        if name.startswith('_'):
            continue
        out_s.write(f"{name.ljust(d['_pad'])} : {d[name]['desc']}\n")
        p1 = d[name]['p1']
        if p1:
            all_p1_vals = sorted(p1.keys(), key=_p1_sort)
            p1_pad = 0
            for p1_el in all_p1_vals:
                p1_pad = max(p1_pad, len(p1_el))
            for p1_el in all_p1_vals:
                out_s.write(f"{' '.ljust(d['_pad']+3)}")
                out_s.write(f"{p1_el.rjust(p1_pad)}")
                out_s.write(f" = {p1[p1_el]}\n")


def main(args_raw, out_s, err_s):
    def err(s, rc=1, indent=''):
        err_s.write(f"{indent}error: {s}\n")
        return rc

    def out(s):
        out_s.write(f"{s}\n")

    name, port = '127.0.0.1', 8000
    cfg_p = Path.home().joinpath('.preamp_remote')
    if cfg_p.is_file():
        cfg = ConfigParser()
        cfg.read(cfg_p)
        name = cfg.get('server', 'name', fallback=name)
        port = cfg.getint('server', 'port', fallback=port)

    p = argparse.ArgumentParser(
        description='Preamp remote command line client',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('--name', default=name,
                   help='REST http hostname/ip')
    p.add_argument('--port', type=int, default=port,
                   help='REST http port')
    p.add_argument('--dotfile', default=False, action='store_true',
                   help=f'auto-generate dotfile {cfg_p}')
    p.add_argument('-d', '--debug', default=False, action='store_true',
                   help='enable debug mode')
    p.add_argument('-l', '--list', default=False, action='store_true',
                   help='list valid commands')
    p.add_argument('-p', '--prefix', default='', metavar='PREFIX',
                   help='list valid commands filtering by prefix')
    p.add_argument('-j', '--json', default=False, action='store_true',
                   help='emit json')
    p.add_argument('commands', nargs='*',
                   help='commands to send')
    args = p.parse_args()
    cl = Client(args.name, args.port)

    if args.dotfile:
        if cfg_p.is_file():
            return err(f"file exists {cfg_p}")
        with open(cfg_p, 'w') as f:
            f.write(_DOTFILE.format(name=args.name, port=args.port))
        return 0

    if not args.json:
        out(f"### server = http://{cl.name}:{cl.port}/")

    if args.prefix or args.list:
        d = cl.commands(args.prefix)
        if d['_err']:
            if args.json:
                out(dumps(d))
            else:
                out(d['_err'])
            return 1
        if args.json:
            out(dumps(d))
        else:
            desc_pretty(d, out_s)
        return 0

    if not args.commands:
        return 0

    data, rc = cl.fetch(args.commands), 0

    if args.json:
        for r in data:
            for rsp in r['responses']:
                if rsp.startswith("ERR "):
                    rc += 1
        out(pformat(data, indent=2))
        return rc

    for r in data:
        if args.debug:
            out(f"{r['request']} ({r['req_raw']})")
        else:
            out(f"{r['request']}")
        for rsp in r['responses']:
            if rsp.startswith("ERR "):
                rc += 1
            out('  ' + rsp)
    return rc


if __name__ == '__main__':
    signal(SIGPIPE, SIG_DFL)  # Suppress broken pipe exceptions.
    try:
        sys.exit(main(sys.argv[1:], sys.stdout, sys.stderr))
    except KeyboardInterrupt:
        sys.exit(1)
