#!/usr/bin/env python3

import sys, codecs, locale
from optparse import OptionParser

# Ensure Unicode output
if sys.version_info < (3,1):
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
else:
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout.detach())


team = "ubuntu-irc-members"   # default team

usage = 'Usage:  %prog [options]'
description = 'Print the members of a team.'
parser = OptionParser(usage=usage, description=description, add_help_option=False)
parser.add_option('-t', '--team', help='Specify team.')
parser.add_option('-m', '--markdown', action='store_true', default=False,
                  help='Print as Markdown.')
parser.add_option('-h', '--help', action='help', help='Print this help text.')
opts, args = parser.parse_args()


if opts.team:
    team = opts.team


cachedir = "~/.cache/launchpadlib"
from launchpadlib.launchpad import Launchpad
launchpad = Launchpad.login_with('Ubuntu IRC Lister', 'production',
                cachedir, version='devel')


try:
    team = launchpad.people[team]
except KeyError:
    print("The team '{}' does not exist on Launchpad.".format(team))
    sys.exit(1)


if not opts.markdown:
    print(u'=== {} ==='.format(team.display_name))
    print(u'++ {} ++'.format(team.web_link))
else:
    print(u'== link:{}[{}] =='.format(team.web_link, team.display_name))

members = {}
for member in team.members:
    if not member.is_team:
        members[member.name] = member

for member in sorted(members):
    member = members[member]

    if not opts.markdown:
        output = u' * {} - {}'.format(member.web_link, member.display_name)
    else:
        output = u' * link:{}[{}]'.format(member.web_link, member.display_name)

    # Check if they're active.
    if member.name.endswith('-deactivatedaccount'):
        output += "'"
        if opts.markdown:
            output = output.replace(' * ', " * '", 1)

    try:
        email = member.preferred_email_address.email
    except ValueError:
        email = None

    if email:
        output += ' <{}>'.format(email)

    print(output)
