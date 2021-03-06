import time
from util import BaseCache


class SimpleCache(BaseCache):
    def __init__(self):
        super(SimpleCache, self).__init__()

    def get_item(self, domain, query_type):
        _cache = self.cache.get(domain)
        if _cache and _cache.get('dt') - int(time.time()) < self.cache_timeout:
            answer = _cache.get(query_type, dict())
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
