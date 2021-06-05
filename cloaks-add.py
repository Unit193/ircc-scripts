#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from optparse import OptionParser

team = "ubuntu-irc-cloaks"   # default team
comment = "IRC cloak set"   # default comment

usage = 'Usage:  %prog [options] [user] ...'
description = 'Add members to a team.'
parser = OptionParser(usage=usage, description=description, add_help_option=False)
parser.add_option('-t', '--team', default=team, help='Specify team.')
parser.add_option('-f', '--file', help='Specify file.')
parser.add_option('-c', '--comment', default=comment, help='Specify comment.')
parser.add_option('-h', '--help', action='help', help='Print this help text.')
opts, args = parser.parse_args()


cachedir = "~/.cache/launchpadlib"
from launchpadlib.launchpad import Launchpad
from launchpadlib.errors import HTTPError
launchpad = Launchpad.login_with('Ubuntu IRC Cloaks Script', 'production',
                cachedir, version='devel')
lp_root_uri = str(launchpad._root_uri)



if args:
    users = set(args)
elif opts.file:
    with open(opts.file) as file:
        users = set(file.read().split())
else:
    users = set(sys.stdin.read().split())

if not users:
    sys.exit()


team = launchpad.people[opts.team]
print("=== {} ===".format(opts.team))

for user in users:
    if user != 'ubuntu-irc-council':
        status = team.addMember(person='%s~%s' % (lp_root_uri, user),
                    status='Approved', comment=opts.comment or None)[1]
        print(" * %s: %s (%s)" % (status, user, opts.comment))
