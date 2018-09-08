import time
import signal
from util import ConfigParse
from dnslib.server import DNSServer, DNSLogger
import importlib


def import_resolver(async_type):
    module_name = 'http_resolver'
    class_name = 'ASyncHTTPResolver' if async_type else 'SyncHTTPResolver'
    return getattr(importlib.import_module(module_name), class_name)


def import_cache(cache_type=None):
    # fake
    moudle_name = 'cache'
    class_name = 'simple_cache'
    return getattr(importlib.import_module(moudle_name), class_name)


class LocalServer():
    def __init__(self):
        self.running = True
        async_type = ConfigParse.async_https
        self.resolver = import_resolver(async_type=async_type)
        self.logger = DNSLogger()

    @property
    def server(self):
        return DNSServer(
            resolver=self.resolver(cache=dict()),
            address=ConfigParse.listen,
            port=ConfigParse.port,
            logger=self.logger)

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
