import os
import re
from requests import get

from core.config import changes
from core.colors import run, que, good, info, end, green
from core.utils import logger


def updater():
    logger('%s Checking for updates' % run)
    latestCommit = get(
        'https://raw.githubusercontent.com/s0md3v/XSStrike/master/core/config.py').text

    if changes not in latestCommit:  # just a hack to see if a new version is available
        changelog = re.search(r"changes = '''(.*?)'''", latestCommit)
        changelog = changelog.group(1).split(
            ';')  # splitting the changes to form a list
        logger('%s A new version of XSStrike is available.' % good)
        logger('%s Changes:' % info)
        for change in changelog:  # print changes
            logger('%s>%s %s' % (green, end, change))

        currentPath = os.getcwd().split('/')  # if you know it, you know it
        folder = currentPath[-1]  # current directory name
        path = '/'.join(currentPath)  # current directory path
        choice = input('%s Would you like to update? [Y/n] ' % que).lower()

        if choice != 'n':
            logger('%s Updating XSStrike' % run)
            os.system(
                'git clone --quiet https://github.com/s0md3v/XSStrike %s' % (folder))
            os.system('cp -r %s/%s/* %s && rm -r %s/%s/ 2>/dev/null' %
                      (path, folder, path, path, folder))
            logger('%s Update successful!' % good)
    else:
        logger('%s XSStrike is up to date!' % good)
