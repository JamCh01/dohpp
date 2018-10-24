import time
import asyncio
from dnslib import QTYPE
from util import BaseHTTPResolver
from dnslib.server import (BaseResolver, RR)
from dns_query import (SyncDNSQuery, AsyncDNSQuery)


class HTTPResolver(BaseHTTPResolver, BaseResolver):
    def __init__(self, query, cache):
        super(HTTPResolver, self).__init__()
        self.query_worker = query()
        self.handler = self.__async_query if 'async' in query.__name__.lower(
        ) else self.__sync_query
        self.cache = cache

    def __async_query(self, params):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        answer = loop.run_until_complete(
            self.query_worker.fetch_dns_query(params=params)).get('Answer')
        return answer

    def __sync_query(self, params):
        answer = self.query_worker.fetch_dns_query(params=params).get('Answer')
        return answer

    def resolve(self, request, handler):
        hostname = str(request.q.qname)
        query_type = request.q.qtype
        _cache = self.cache.get_item(domain=hostname, query_type=query_type)
        if _cache:
            answer = _cache
        else:
            params = dict(name=hostname, type=query_type, edns=self.edns)
            answer = self.handler(params=params)
            self.cache.set_item(
                domain=hostname, query_type=query_type, data=answer)

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
