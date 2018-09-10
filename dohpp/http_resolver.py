import time
import asyncio
from dnslib import QTYPE
from util import BaseHTTPResolver
from dnslib.server import (BaseResolver, RR)
from dns_query import (SyncDNSQuery, AsyncDNSQuery)


class HTTPResolver(BaseHTTPResolver, BaseResolver):
    def __init__(self, query, cache=dict()):
        super(HTTPResolver, self).__init__()
        self.query_worker = query()
        self.handler = self.__async_query if 'async' in query.__name__.lower(
        ) else self.__sync_query
        self.cache = cache

    def __async_query(self, url):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        answer = loop.run_until_complete(
            self.query_worker.fetch_dns_query(url=url)).get('Answer')
        return answer

    def __sync_query(self, url):
        answer = self.query_worker.fetch_dns_query(url=url).get('Answer')
        return answer

    def resolve(self, request, handler):
        hostname = str(request.q.qname)
        query_type = request.q.qtype
        _cache = self.cache.get(hostname)

        if _cache and _cache.get('dt') - int(time.time()) < self.cache_timeout:
            answer = _cache.get(query_type)
        else:
            url = self.google_dns_url.format(
                ext='name={name}&type={type}'.format(
                    name=hostname, type=query_type))
            answer = self.handler(url=url)
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
