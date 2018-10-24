import time
import signal
import importlib
from util import ConfigParse
from cache import SimpleCache
from http_resolver import HTTPResolver
from dnslib.server import DNSServer, DNSLogger

__dns_query__ = ['AsyncDNSQuery', 'SyncDNSQuery']


def import_query():
    module_name = 'dns_query'
    class_name = 'AsyncDNSQuery' if ConfigParse.async_https else 'SyncDNSQuery'
    return getattr(importlib.import_module(module_name), class_name)


class LocalServer():
    def __init__(self):
        self.running = True

    def start(self):
        server = DNSServer(
            resolver=HTTPResolver(query=import_query(), cache=SimpleCache()),
            address=ConfigParse.listen,
            port=ConfigParse.port,
            logger=DNSLogger())
        server.start_thread()
        while self.running:
            time.sleep(5)
        server.stop()

    def stop(self, signal, handler):
        self.running = False


def main():
    localserver = LocalServer()
    signal.signal(signal.SIGINT, localserver.stop)
    signal.signal(signal.SIGTERM, localserver.stop)
    localserver.start()


if '__main__' == __name__:
    main()
