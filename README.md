# dohpp
dns over https by pure python

## dohpp是什么
dohpp的全名是`DNS over HTTPS by Pure Python`，它是由Python构建的，依赖于GoogleDNS的DOH服务。目的是为了避免DNS抢答或DNS污染。

## 如何使用？
### 1. 下载源码
git clone
```
git clone https://github.com/JamCh01/dohpp.git
```
### 2. 安装依赖
```
cd dohpp
pip install -r requirements.txt
```
**请注意，因为使用了asyncio，所以仅支持Python3。**
### 3. 更改配置
dohpp提供了默认的`config.json`，它位于`dohpp/dohpp/config.json`。请根据实际情况进行修改：
```json
{
    "proxy": {
        "addr": "127.0.0.1",
        "port": 1080,
        "auth": ""
    },
    "google_dns_url": "https://dns.google.com/resolve?{ext}",
    "cache_timeout": 1800,
    "async_https": false,
    "listen": "127.0.0.1",
    "port": 53,
    "local": ""
}
```
#### proxy
proxy字段制定了socks5的代理，因为某些特殊的原因使用GoogleDNS需要代理。
#### cache_timeout
查询后的域名解析记录缓存时间，默认1800s。
#### async_https
使用异步HTTPS请求来代替同步HTTPS请求，默认false。
#### listen
dohpp工作的IP
#### port
dohpp工作的端口
#### local
edns使用，目的是获得最合理的解析记录，默认为空。

当然这些配置可以不设置，或者丢失部分记录，dohpp会使用默认的配置进行工作。

#### 4. 使用
```
python /path/to/dohp/pserver.py
```
之后更改本机DNS服务器为`127.0.0.1`或配置中listen的数值。
It works well!