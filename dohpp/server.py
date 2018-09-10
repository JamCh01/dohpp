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


def import_cache(cache_type=None):
    # fake
    moudle_name = 'cache'
    class_name = 'simple_cache'
    return getattr(importlib.import_module(moudle_name), class_name)


class LocalServer():
    def __init__(self):
        self.running = True

    @property
    def server(self):
        return DNSServer(
            resolver=HTTPResolver(
                query=import_query(), cache=SimpleCache(timeout=1800)),
            address=ConfigParse.listen,
            port=ConfigParse.port,
            logger=DNSLogger())

    def start(self):
        self.server.start_thread()
        while self.running:
            time.sleep(5)
        self.server.stop()

    def stop(self, signal, handler):
        self.running = False


def main():
    localserver = LocalServer()
    signal.signal(signal.SIGINT, localserver.stop)
    localserver.start()


if '__main__' == __name__:
    main()
