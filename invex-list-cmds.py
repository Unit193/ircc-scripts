#!/usr/bin/env python3

import sys
from optparse import OptionParser

team = "ubuntu-core-ops"   # default team
channels = ("#ubuntu-ops-team", "#ubuntu-ops-monitor")   # default invex channels

usage = 'Usage:  %prog [options]'
description = 'Print invex commands for the members of a team and its subteams.'
parser = OptionParser(usage=usage, description=description, add_help_option=False)
parser.add_option('-t', '--team', help='Specify team.')
parser.add_option('-d', '--devel', action='store_true', default=False,
                  help='Get devel team.')
parser.add_option('-o', '--operators', action='store_true', default=False,
                  help='Get all operators.')
parser.add_option('-c', '--chanonly', action='store_true',
                  default=False, help='Get only channel teams.')
parser.add_option('-x', '--channel', help='Specify invex channel.')
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

if opts.channel:
    channels = (opts.channel,)


cachedir = "~/.cache/launchpadlib"
from launchpadlib.launchpad import Launchpad
launchpad = Launchpad.login_anonymously('Ubuntu IRC Lister', 'production',
                cachedir, version='devel')


def get_op_nicks(team, nicks):
    for member in team.members:
        if member.is_team or member.name.endswith('-deactivatedaccount'):
            continue

        try:
            for nick in member.irc_nicknames:
                network = nick.network.lower()
                if 'libera' in network:
                    nicks.add(nick.nickname)
                    break
        except:
            pass

    return nicks


try:
    team = launchpad.people[team]
except KeyError:
    print("The team '{}' does not exist on Launchpad.".format(team))
    sys.exit(1)

teams = {team.name: team}
for sub_team in team.sub_teams:
    teams[sub_team.name] = sub_team

ops = set([])
for team in teams:
    team = teams[team]
    if not (opts.chanonly and team.display_name[0] != '#') \
            and not team.display_name.startswith(('#edubuntu', '#ubuntu-mythtv')):
        ops = get_op_nicks(team, ops)


irccops, kcops = set([]), set([])
for channel in sorted(channels):
    if channel in ('#ubuntu-ops-team', '#ubuntu-ops-monitor'):
        if not irccops:
            irccops = get_op_nicks(launchpad.people['ubuntu-irc-council'], irccops)
        if not kcops:
            kcops = get_op_nicks(launchpad.people['kubuntu-council'], kcops)

    for op in sorted(ops, key=str.casefold):
        print("/mode {} +I $a:{}".format(channel, op))
    print('')
