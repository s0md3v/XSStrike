import re
import sys
from core.make_request import make_request

blind_params = ['redirect','redir','url','link','goto','debug','_debug','test','get','index','src','source','file',
'frame','config','new','old','var','rurl','return_to','_return','returl','last','text','load','email',
'mail','user','username','password','pass','passwd','first_name','last_name','back','href','ref','data','input',
'out','net','host','address','code','auth','userid','auth_token','token','error','keyword','key','q','query','aid',
'bid','cid','did','eid','fid','gid','hid','iid','jid','kid','lid','mid','nid','oid','pid','qid','rid','sid',
'tid','uid','vid','wid','xid','yid','zid','cal','country','x','y','topic','title','head','higher','lower','width',
'height','add','result','log','demo','example','message']

good = '\033[32m[+]\033[0m'
green = '\033[92m'
end = '\033[0m'
run = '\033[97m[~]\033[0m'

def paramfinder(url, method, paranames, paravalues, xsschecker, cookie):
    response = make_request(url, '', method, cookie)
    matches = re.findall(r'<input.*?name=\'(.*?)\'.*?>|<input.*?name="(.*?)".*?>', response)
    for match in matches:
        try:
            found_param = match[1]
        except UnicodeDecodeError:
            continue
        print('%s Heuristics found a potentially valid parameter: %s%s%s. Priortizing it.' % (good, green, found_param, end))
        if found_param in blind_params:
            blind_params.remove(found_param)
        blind_params.insert(0, found_param)
    progress = 0
    for param in blind_params:
        progress = progress + 1
        sys.stdout.write('\r%s Parameters checked: %i/%i' % (run, progress, len(blind_params)))
        sys.stdout.flush()
        if param not in paranames:
            if method == 'GET':
                response = make_request(url, '?' + param + '=' + xsschecker, method, cookie)
            else:
                response = make_request(url, param + '=' + xsschecker, method, cookie)
            if ('\'%s\'' % xsschecker or '"%s"' % xsschecker or ' %s ' % xsschecker) in response:
                print('\n%s Valid parameter found : %s%s%s' % (good, green, param, end))
                paranames.append(param)
                paravalues.append('')
