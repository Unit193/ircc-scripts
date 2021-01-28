#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from optparse import OptionParser

team = "ubuntu-irc-cloaks"   # default team
comment = "IRC cloaks cleanup"   # default comment

usage = 'Usage:  %prog [options] [user] ...'
description = 'Remove members of a team.'
parser = OptionParser(usage=usage, description=description, add_help_option=False)
parser.add_option('-t', '--team', default=team, help='Specify team.')
parser.add_option('-f', '--file', help='Specify file.')
parser.add_option('-c', '--comment', default=comment, help='Specify comment.')
parser.add_option('-h', '--help', action='help', help='Print this help text.')
opts, args = parser.parse_args()


if args:
    users = args
elif opts.file:
    with open(opts.file) as file:
        users = file.read().split()
else:
    users = sys.stdin.read().split()

if not users:
    sys.exit()


cachedir = "~/.cache/launchpadlib"
from launchpadlib.launchpad import Launchpad
from launchpadlib.errors import HTTPError
launchpad = Launchpad.login_with('Ubuntu IRC Cloaks Removal Script', 'production', cachedir, version='devel')
lp_root_uri = str(launchpad._root_uri)


for user in users:
    try:
        member = launchpad.load('%s~%s/+member/%s' % (lp_root_uri, opts.team, user))
    except HTTPError as error:
	if error.response['status'] == '404':
	    print("No member of '%s': '%s'" % (opts.team, user))
	else:
	    print("HTTP error %s: '%s'" % (error.response['status'], user))
    else:
        print("Removing from '%s': '%s' (%s)" % (opts.team, user, opts.comment))
        member.setStatus(status='Deactivated', comment=opts.comment)
