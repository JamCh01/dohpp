import json
import time


class ConfigParse():
    config = json.load(open('config.json', 'r'))
    google_dns_url = config.get('google_dns_url',
                                'https://dns.google.com/resolve?{ext}')
    cache_timeout = config.get('cache_timeout', 1800)
    proxy = config.get('proxy', {
        'addr': '127.0.0.1',
        'port': 1080,
        'auth': '',
    })
    proxy_addr = proxy.get('addr')
    proxy_port = proxy.get('port')
    proxy_auth = proxy.get('auth')
    listen = config.get('listen', '127.0.0.1') or '127.0.0.1'
    port = config.get('port', 53) or 53
    async_https = config.get('async_https', False)
    edns = config.get('local', '0.0.0.0/0') or '0.0.0.0/0'


class BaseDNSQuery():
    def __init__(self):
        self.headers = {'Content-Type': 'application/json'}
        self.proxy_addr = ConfigParse.proxy_addr
        self.proxy_port = ConfigParse.proxy_port
        self.proxy_auth = ConfigParse.proxy_auth
        socks5h_str = 'socks5h://{auth}{host}:{port}'.format(
            auth='' if not self.proxy_auth else self.proxy_auth + '@',
            host=self.proxy_addr,
            port=self.proxy_port)
        self.proxy = {
            'http': socks5h_str,
            'https': socks5h_str,
        }


class BaseHTTPResolver():
    def __init__(self):
        self.google_dns_url = ConfigParse.google_dns_url
        self.cache_timeout = ConfigParse.cache_timeout
        self.proxy = ConfigParse.proxy
        self.edns = ConfigParse.edns
        self.ext = 'name={name}&type={type}&edns_client_subnet={edns}'


class BaseCache():
    def __init__(self, timeout=1800):
        # example by dict
        self.cache = dict()
        self.cache_timeout = timeout or ConfigParse.cache_timeout

    def get_item(self, domain, query_type):
        _cache = self.cache.get(domain)
        if _cache and _cache.get('dt') - int(time.time()) < self.cache_timeout:
            answer = _cache.get(query_type)
        else:
            answer = dict()
        return answer

    def set_item(self, domain, query_type, data):
        if domain not in self.cache:
            self.cache.setdefault(domain, dict())
        self.cache.get(domain).update({
            query_type: data,
            'dt': int(time.time()),
        })
        return
