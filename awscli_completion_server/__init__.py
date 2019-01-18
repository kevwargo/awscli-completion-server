import sys
import json
import argparse
import traceback
from struct import pack, unpack
from threading import Thread
from socket import socket, SOL_SOCKET, SO_REUSEADDR, SHUT_RDWR
from awscli.completer import Completer


def run():
    parser = argparse.ArgumentParser(prog='aws-comp-srv')
    parser.add_argument('-a', '--address', required=True, help='An IP address for the server to listen on')
    parser.add_argument('-p', '--port', required=True, type=_port, help='A TCP port for the server to listen on')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-l', '--log')
    ns = parser.parse_args(sys.argv[1:])
    start_server(ns)


def _port(val):
    port = int(val)
    if port < 1 and port > 65535:
        raise ValueError('TCP port must be in 1-65535 range')
    return port


def start_server(ns):
    clients = []
    sock = socket()
    try:
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind((ns.address, ns.port))
        sock.listen(5)

        completer = Completer()

        ns.logfile = None
        if ns.log:
            ns.logfile = open(ns.log, 'a')

        while True:
            c, a = sock.accept()
            log(ns, f'New client from {a}')
            clients.append(c)
            ClientThread(c, a, completer, ns).start()
    except:
        if ns.logfile:
            try:
                traceback.print_exc(file=ns.logfile)
                traceback.print_stack(file=ns.logfile)
            except:
                traceback.print_exc()
                traceback.print_stack()
    finally:
        for c in clients:
            try:
                c.shutdown(SHUT_RDWR)
                c.close()
            except:
                pass
        try:
            sock.shutdown(SHUT_RDWR)
            sock.close()
        except:
            pass
        if ns.log:
            try:
                ns.logfile.close()
            except:
                pass


def log(ns, msg):
    if ns.verbose:
        print(msg)
    if ns.logfile:
        print(msg, file=ns.logfile, flush=True)


class ClientThread(Thread):

    def __init__(self, sock, address, completer, ns):
        super().__init__()
        self.sock = sock
        self.address = address
        self.completer = completer
        self.ns = ns

    def run(self):
        while True:
            sizebuf = self.sock.recv(4)
            if len(sizebuf) < 4:
                return
            size = unpack('<I', sizebuf)[0]
            req = b''
            while len(req) < size:
                rcvd = self.sock.recv(size - len(req))
                if not rcvd:
                    log(ns, f'Client {self.address} received empty response')
                    return
                req += rcvd
            args = json.loads(req.decode())
            log(ns, f'Client {self.address} received {args}')
            completions = self.completer.complete(*args)
            log(ns, f'Sending {completions} to client {self.address}')
            resp = json.dumps(completions).encode()
            self.sock.send(pack('<I', len(resp)) + resp)
