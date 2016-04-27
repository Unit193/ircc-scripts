#!/usr/bin/python
#
# Author: C de-Avillez <hggdh2@ubuntu.com>
# Copyright (C) 2016 C de-Avillez <hggdh2@ubuntu.com>
# Licence: GPLV3
#
# rm-ubuntu-cloak: remove a person from the ubuntu-irc-cloaks team.
# stdin is used (right now). So if you have one single removal, run
#   echo <user> | rm-ubuntu-cloak.py
#
# Will, eventually, be expanded to deal with all IRC team (and will
# receive parameters for them)
#
# NOTE: for whatever reason, it is failing with Python3 on OAuth. Will
#       look at this later.


from launchpadlib.errors import HTTPError
from launchpadlib.launchpad import Launchpad
import sys

# TEAM will be a parameter later on, right now a constant
TEAM = 'ubuntu-irc-cloaks'
# login to LP; this will initiate an OAuth request that may require
# the user to look at the browser
lp = Launchpad.login_with('rm_ubuntu_cloaks', 'production', version='devel')
LP_ROOT = str(lp._root_uri)


def get_input():
    '''
    reads one more user to be worked on from stdin
    :return: user
    :rtype: basestring
    '''
    user = sys.stdin.readline().rstrip()
    return user.lower()


# mainline
lpid = get_input()
while lpid:
    print("Working on %s" % lpid)
    try:
        try:
            URI = LP_ROOT + '~%s/+member/%s' % (TEAM, lpid)
            member = lp.load(URI)
        except HTTPError as error:
            print("got HTTP error %s when loading LP for %s" % (error.response['status'], lpid))
        else:
            member.setStatus(status='Deactivated', comment='irc cloaks cleanup')
    except HTTPError as error:
        if error.response['status'] != '404':
            print('barfed on %s...' % lpid)
    except ValueError:
        print('%s does not seem to be a valid user on LP' % lpid)
    lpid = get_input()

print("Done.")
