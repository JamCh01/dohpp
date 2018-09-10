import asyncio
import requests
from functools import partial
from util import BaseDNSQuery


class SyncDNSQuery(BaseDNSQuery):
    def fetch_dns_query(self, url):
        if url.endswith('in-addr.arpa'):
            return {}
        r = requests.get(url=url, proxies=self.proxy, headers=self.headers)
        if r.status_code == 200:
            return r.json()
        else:
            return {}


class AsyncDNSQuery(BaseDNSQuery):
    async def fetch_dns_query(self, url):
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        requests_with_proxies = partial(
            requests.get, proxies=self.proxy, headers=self.headers)
        r = await loop.run_in_executor(None, requests_with_proxies, url)
        print(r)
        if r.status_code == 200:
            return r.json()
        else:
            return {}
