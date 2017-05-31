#!/usr/bin/env python3
# see LICENSE file for copyright and license details

"""
module to pool and download Release files when needed
"""

import subprocess
from os.path import join
import requests

from lib.net import download
from lib.parse import parse_release, get_time, get_date


roots = {
    'devuan': {
        'local': 'spool/devuan/dists/jessie',
        'remote': 'http://auto.mirror.devuan.org/devuan/dists/jessie',
    },
    'debian': {
        'local': 'spool/debian/dists/jessie',
        'remote': 'http://ftp.debian.org/debian/dists/jessie',
    },
    'debian-sec': {
        'local': 'spool/dists/jessie/updates',
        'remote': 'http://security.debian.org/dists/jessie/updates',
    },
}

release_file = 'Release'


def merge_files(repo, relfile):
    """
    Loads the local release and call the merge process
    """
    print('Loading Release')
    rel = join(roots[repo]['local'], relfile)
    release_contents = open(rel).read()

    hashes = parse_release(release_contents)

    for k in hashes:
        # if k.endswith('Packages.gz'):
        if k.endswith('/binary-armhf/Packages.gz'):
            # skip empty files
            # TODO: probably best to copy it in place when this occurs
            if hashes[k] == 'f61f27bd17de546264aa58f40f3aafaac7021e0ef69c17f6b1b4cd7664a037ec':
                print('Skipping %s' % k)
                continue

            subprocess.run(['./amprolla-merge', k])


local_rel = join(roots['devuan']['local'], release_file)
remote_rel = join(roots['devuan']['remote'], release_file)

# Possibly use this var to check for changed hashes
local_contents = open(local_rel).read()
local_date = get_date(local_contents)

r = requests.get(remote_rel)
remote_contents = r.text
remote_date = get_date(remote_contents)

print('Local date: %s' % local_date)
print('Remote date: %s' % remote_date)

if get_time(remote_date) > get_time(local_date):
    # dump new release in place and merge
    # NOTE: when testing, watch out because you lose the old Release file in
    # spool
    print('Remote is newer')
    download(remote_rel, local_rel)
    merge_files('devuan', local_rel)