import aiohttp
import asyncio
import requests
from util import BaseDNSQuery
from aiosocksy.connector import ProxyConnector, ProxyClientRequest


class SyncDNSQuery(BaseDNSQuery):
    def __init__(self):
        super(SyncDNSQuery, self).__init__()
        socks5h_str = 'socks5h://{auth}{host}:{port}'.format(
            auth='' if not self.proxy_auth else self.proxy_auth + '@',
            host=self.proxy_addr,
            port=self.proxy_port)
        self.proxy = {
            'http': socks5h_str,
            'https': socks5h_str,
        }

    def fetch_dns_query(self, url):
        if url.endswith('in-addr.arpa'):
            return {}
        r = requests.get(url=url, proxies=self.proxy, headers=self.headers)
        if r.status_code == 200:
            return r.json()
        else:
            return {}


class AsyncDNSQuery(BaseDNSQuery):
    def __init__(self):
        self.connector = ProxyConnector()

    async def fetch_dns_query(self, url):
        async with aiohttp.ClientSession(
                connector=self.connector,
                request_class=ProxyClientRequest) as session:
            async with session.get(
                    url=url, headers=self.headers, proxy=self.proxy) as resp:
                return await resp.text()
