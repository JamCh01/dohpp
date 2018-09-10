import time
import asyncio
from dnslib import QTYPE
from util import BaseHTTPResolver
from dnslib.server import (BaseResolver, RR)
from dns_query import (SyncDNSQuery, AsyncDNSQuery)


class AsyncHTTPResolver(BaseHTTPResolver, BaseResolver):
    def __init__(self, cache=dict()):
        super(AsyncHTTPResolver, self).__init__()
        self.query_handler = AsyncDNSQuery()
        self.cache = cache

    def resolve(self, request, handler):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        hostname = str(request.q.qname)
        query_type = request.q.qtype
        _cache = self.cache.get(hostname)
        url = self.google_dns_url.format(ext='name={name}&type={type}'.format(
            name=hostname, type=query_type))
        answer = loop.run_until_complete(
            self.query_handler.fetch_dns_query(url=url)).get('Answer')
        print(answer)


class SyncHTTPResolver(BaseHTTPResolver, BaseResolver):
    def __init__(self, cache=dict()):
        super(SyncHTTPResolver, self).__init__()
        self.query_handler = SyncDNSQuery()
        self.cache = cache

    def resolve(self, request, handler):
        hostname = str(request.q.qname)
        query_type = request.q.qtype
        _cache = self.cache.get(hostname)
        url = self.google_dns_url.format(ext='name={name}&type={type}'.format(
            name=hostname, type=query_type))
        if _cache and _cache.get('dt') - int(time.time()) < self.cache_timeout:
            answer = _cache.get(query_type)
        else:
            answer = self.query_handler.fetch_dns_query(url=url).get('Answer')
            if hostname not in self.cache:
                self.cache.setdefault(hostname, dict())
            self.cache.get(hostname).update({
                query_type: answer,
                'dt': int(time.time()),
            })

        reply = request.reply()
        for record in answer:
            rtype = QTYPE[int(record['type'])]
            zone = '{name} {TTL} {rtype} {data}'.format(
                name=str(record['name']),
                TTL=record['TTL'],
                rtype=rtype,
                data=str(record['data']))
            reply.add_answer(*RR.fromZone(zone))
        return reply
