import asyncio
import requests
from functools import partial
from util import BaseDNSQuery


class SyncDNSQuery(BaseDNSQuery):
    def fetch_dns_query(self, params):
        r = requests.get(
            url=self.url, params=params, proxies=self.proxy, headers=self.headers)
        if r.status_code == 200:
            return r.json()
        else:
            return {}


class AsyncDNSQuery(BaseDNSQuery):
    async def fetch_dns_query(self, params):
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        requests_with_proxies = partial(
            requests.get,
            params=params,
            proxies=self.proxy,
            headers=self.headers)
        r = await loop.run_in_executor(None, requests_with_proxies, self.url)
        if r.status_code == 200:
            return r.json()
        else:
            return {}
