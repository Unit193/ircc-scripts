#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, codecs, locale
from optparse import OptionParser

# Ensure Unicode output
if sys.version_info < (3,1):
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
else:
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout.detach())


team = "ubuntu-core-ops"   # default team

usage = 'Usage:  %prog [options]'
description = 'Print the members of a team and its subteams.'
parser = OptionParser(usage=usage, description=description, add_help_option=False)
parser.add_option('-t', '--team', help='Specify team.')
parser.add_option('-d', '--devel', action='store_true', default=False,
                  help='Get devel team.')
parser.add_option('-o', '--operators', action='store_true', default=False,
                  help='Get all operators.')
parser.add_option('-a', '--applicants', action='store_true', default=False,
                  help='Get applicants.')
parser.add_option('-c', '--chanonly', action='store_true',
                  default=False, help='Get only channel teams.')
parser.add_option('-m', '--markdown', action='store_true', default=False,
                  help='Print as Markdown.')
parser.add_option('-h', '--help', action='help', help='Print this help text.')
opts, args = parser.parse_args()


if opts.team:
    team = opts.team

if opts.devel and 'devel' not in team:
    if team.endswith('-ops'):
        team = team.rsplit('-', 1)[0] + '-devel-ops'
    else:
        team += '-devel'

if opts.operators:
    if not opts.team and not opts.devel:
        team = "ubuntu-ops"
    opts.chanonly = True


cachedir = "~/.cache/launchpadlib"
from launchpadlib.launchpad import Launchpad
launchpad = Launchpad.login_anonymously('Ubuntu IRC Lister', 'production',
                cachedir, version='devel')


def drop_ops(teamname):
    if teamname.startswith('irc-') and teamname.endswith('-ops'):
        return teamname.rsplit('-', 1)[0]
    return teamname


try:
    team = launchpad.people[team]
except KeyError:
    print("The team '{}' does not exist on Launchpad.".format(team))
    sys.exit(1)

teams = {team.name: team}
for sub_team in team.sub_teams:
    teams[sub_team.name] = sub_team


if opts.applicants:
    allops = []
    for team in list(teams.values()):
        if not (opts.chanonly and team.display_name[0] != '#'):
            for member in team.members:
                allops.append(member.name)


for team in sorted(teams, key=drop_ops):
    team = teams[team]

    if not (opts.chanonly and team.display_name[0] != '#'):
        if opts.applicants and not team.proposed_members:
            continue

        if not opts.markdown:
            print(u'=== {} ==='.format(team.display_name))
            print(u'++ {} ++'.format(team.web_link))
        else:
            print(u'== link:{}[{}] =='.format(team.web_link, team.display_name))

        members = {}
        for member in team.members if not opts.applicants \
                else team.proposed_members:
            members[member.name] = member

        for member in sorted(members):
            member = members[member]

            nicks = []
            try:
                for nick in member.irc_nicknames:
                    network = nick.network.lower()
                    if 'libera' in network:
                        nicks.append(nick.nickname)
                gone = False
            except:
                gone = True

            if not opts.markdown:
                output = u' * {} - {}'.format(member.web_link, member.display_name)
            else:
                output = u' * link:{}[{}]'.format(member.web_link, member.display_name)

            # Check if they're an OP in one of the other channels.
            if opts.applicants and member.name in allops:
                output += '*'
                if opts.markdown:
                    output = output.replace(' * ', ' * *', 1)

            # Check if they're active.
            if member.name.endswith('-deactivatedaccount') or gone:
                output += "'"
                if opts.markdown:
                    output = output.replace(' * ', " * '", 1)

            if nicks:
                print(u'{} ({})'.format(output, ', '.join(nicks)))
            else:
                print(output)

        print('')
