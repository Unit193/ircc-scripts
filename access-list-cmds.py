#!/usr/bin/env python3

import sys
from optparse import OptionParser

team = "ubuntu-core-ops"   # default team

usage = 'Usage:  %prog [options]'
description = 'Print ACL commands for the members of a team and its subteams.'
parser = OptionParser(usage=usage, description=description, add_help_option=False)
parser.add_option('-t', '--team', help='Specify team.')
parser.add_option('-d', '--devel', action='store_true', default=False,
                  help='Get devel team.')
parser.add_option('-o', '--operators', action='store_true', default=False,
                  help='Get all operators.')
parser.add_option('-c', '--chanonly', action='store_true',
                  default=False, help='Get only channel teams.')
parser.add_option('-x', '--channel', help='Specify channel.')
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

channels = {}
if opts.channel:
    channels[opts.channel] = {}
    if not opts.team:
        team = 'irc-{}-ops'.format(opts.channel.lstrip('#'))


cachedir = "~/.cache/launchpadlib"
from launchpadlib.launchpad import Launchpad
launchpad = Launchpad.login_anonymously('Ubuntu IRC Lister', 'production',
                cachedir, version='devel')


def get_op_nicks(team, nicks, group='op'):
    for member in team.members:
        if member.is_team:
            if member.display_name.startswith('#') \
                    and not member.display_name.startswith(('#edubuntu', '#ubuntu-mythtv')):
                nicks["$chanacs:{}".format(member.display_name.split()[0])] = group
            continue
        elif member.name.endswith('-deactivatedaccount'):
            continue

        try:
            for nick in member.irc_nicknames:
                network = nick.network.lower()
                if 'libera' in network:
                    nicks[nick.nickname] = group
                    break
        except:
            pass

    return nicks


def get_cop_nicks(ops, cops, team, group):
    if not cops:
        cops = get_op_nicks(launchpad.people[team], cops, group)
    for cop in list(cops.keys()):
        ops[cop] = cops[cop]
    return ops


try:
    team = launchpad.people[team]
except KeyError:
    print("The team '{}' does not exist on Launchpad.".format(team))
    sys.exit(1)

teams = {team.name: team}
for sub_team in team.sub_teams:
    if sub_team.name != 'ubuntu-irc-council':
        teams[sub_team.name] = sub_team

ops = {}
for team in teams:
    team = teams[team]
    if opts.chanonly and team.display_name[0] != '#':
        continue
    elif opts.channel:
        channels[opts.channel] = get_op_nicks(team, ops)
    elif not team.display_name.startswith(('#edubuntu', '#ubuntu-mythtv')):
        channel = team.display_name.split()[0]
        if channel == '#ubuntu+1':
            channel = "#ubuntu-next"
        channels[channel] = get_op_nicks(team, {})


coreops, kcops = {}, {}
for channel in sorted(list(channels.keys())):
    ops = channels[channel]

    print("template {} founder -*+AFRefiorstv".format(channel))
    print("template {} op -*+Aiotv".format(channel))
    print("template {} bot -*+eor".format(channel))
    if channel.startswith('#kubuntu'):
        print("template {} kcouncil -*+Aeiortv".format(channel))
        ops = get_cop_nicks(ops, kcops, 'kubuntu-council', 'kcouncil')
    elif channel == '#ubuntu-ops':
        print("template {} team -*+AViv".format(channel))
        ops = get_cop_nicks(ops, coreops, 'ubuntu-core-ops', 'team')

    print("flags {} UbuntuIrcCouncil founder".format(channel))
    print("flags {} *!*@libera/staff/* op".format(channel))
    for bot in ('Drone', 'ubottu'):
        print("flags {} {} bot".format(channel, bot))
    for op in sorted(ops, key=str.casefold):
        print("flags {} {} {}".format(channel, op, ops[op]))
    print('')
