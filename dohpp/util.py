import json
import time


class ConfigParse():
    config = json.load(open('config.json', 'r'))
    dohpp_settings = config.get('dohpp_settings')
    google_dns_settings = config.get('google_dns_settings')
    proxy_addr = dohpp_settings.get('proxy_addr', '127.0.0.1') or '127.0.0.1'
    proxy_port = dohpp_settings.get('proxy_port', 1080) or 1080
    proxy_auth = dohpp_settings.get('proxy_auth', None)

    proxy = 'socks5h://{auth}{host}:{port}'.format(
        auth='' if not proxy_auth else proxy_auth + '@',
        host=proxy_addr,
        port=proxy_port)

    cache_timeout = dohpp_settings.get('cache_timeout', 1800)
    listen = dohpp_settings.get('listen', '127.0.0.1') or '127.0.0.1'
    port = dohpp_settings.get('port', 53) or 53
    async_https = dohpp_settings.get('async_https', False)
    edns = google_dns_settings.get('local', '0.0.0.0/0') or '0.0.0.0/0'


class BaseDNSQuery():
    def __init__(self):
        self.url = 'https://dns.google.com/resolve'
        self.headers = {'Content-Type': 'application/json'}
        socks5h = ConfigParse.proxy
        self.proxy = {
            'http': socks5h,
            'https': socks5h,
        }


class BaseHTTPResolver():
    def __init__(self):
        self.cache_timeout = ConfigParse.cache_timeout
        self.proxy = ConfigParse.proxy
        self.edns = ConfigParse.edns
        self.ext = 'name={name}&type={type}&edns_client_subnet={edns}'


class BaseCache():
    def __init__(self):
        # example by dict
        self.cache = dict()
        self.cache_timeout = ConfigParse.dohpp_settings.get(
            'cache_timeout', 1800) or 1800

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
