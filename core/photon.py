# Let's import what we need
from re import findall
import concurrent.futures
from urllib.parse import urlparse

from core.colors import run
from core.zetanize import zetanize
from core.requester import requester
from core.utils import getUrl, getParams

def photon(seedUrl, headers, level, threadCount, delay, timeout):
    forms = [] # web forms
    processed = set() # urls that have been crawled
    storage = set() # urls that belong to the target i.e. in-scope
    schema = urlparse(seedUrl).scheme
    host = urlparse(seedUrl).netloc
    main_url = schema + '://' + host
    storage.add(seedUrl)
    def rec(target):
        processed.add(target)
        print ('%s Parsing %s' % (run, target))
        url = getUrl(target, True)
        params = getParams(target, '', True)
        if '=' in target:
            inps = []
            for name, value in params.items():
                inps.append({'name': name, 'value': value})
            forms.append({0: {'action': url, 'method': 'get', 'inputs': inps}})
        response = requester(url, params, headers, True, delay, timeout).text
        forms.append(zetanize(response))
        matches = findall(r'<[aA].*href=["\']{0,1}(.*?)["\']', response)
        for link in matches: # iterate over the matches
            link = link.split('#')[0] # remove everything after a "#" to deal with in-page anchors
            if link[:4] == 'http':
                if link.startswith(main_url):
                    storage.add(link)
            elif link[:2] == '//':
                if link.split('/')[2].startswith(host):
                    storage.add(schema + link)
            elif link[:1] == '/':
                storage.add(main_url + link)
            else:
                storage.add(main_url + '/' + link)
    for x in range(level):
        urls = storage - processed
        threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=threadCount)
        futures = (threadpool.submit(rec, url) for url in urls)
        for i, _ in enumerate(concurrent.futures.as_completed(futures)):
            pass
    return [forms, processed]
