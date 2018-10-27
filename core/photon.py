# Let's import what we need
import tld
import sys
import json
from re import findall
import concurrent.futures
from urllib.parse import urlparse # for python3

from core.colors import run
from core.zetanize import zetanize
from core.requester import requester
from core.utils import getUrl, getParams

def photon(main_url, url, headers):
    urls = set() # urls found
    forms = [] # web forms
    processed = set() # urls that have been crawled
    storage = set() # urls that belong to the target i.e. in-scope
    host = urlparse(url).netloc
    url = getUrl(url, '', True)
    schema = urlparse(main_url).scheme
    params = getParams(url, '', True)
    response = requester(url, params, headers, True, 0).text
    forms.append(zetanize(response))
    matches = findall(r'<[aA].*href=["\']{0,1}(.*?)["\']', response)
    for link in matches: # iterate over the matches
        link = link.split('#')[0] # remove everything after a "#" to deal with in-page anchors
        if link[:4] == 'http':
            if link.startswith(main_url):
                urls.add(link)
        elif link[:2] == '//':
            if link.split('/')[2].startswith(host):
                urls.add(schema + link)
        elif link[:1] == '/':
            urls.add(main_url + link)
        else:
            urls.add(main_url + '/' + link)
    def rec(target):
        print ('%s Parsing %s' % (run, target))
        url = getUrl(target, '', True)
        params = getParams(target, '', True)
        if '=' in target:
            inps = []
            for name, value in params.items():
                inps.append({'name': name, 'value': value})
            forms.append({0: {'action': url, 'method': 'get', 'inputs': inps}})
        response = requester(url, params, headers, True, 0).text
        forms.append(zetanize(response))
    from core.config import threadCount
    threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=threadCount)
    futures = (threadpool.submit(rec, url) for url in urls)
    for i, _ in enumerate(concurrent.futures.as_completed(futures)):
        pass
    return forms
