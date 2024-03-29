#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, codecs, locale
from optparse import OptionParser

# Ensure Unicode output
if sys.version_info < (3,1):
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
else:
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout.detach())


target = "ubuntu-irc-cloaks"   # default target team
reference = "ubuntumembers"   # default reference team

usage = 'Usage:  %prog [options]'
description = 'Print any members of a target team who are not in the reference team.'
parser = OptionParser(usage=usage, description=description, add_help_option=False)
parser.add_option('-t', '--target', metavar='TEAM', default=target,
                  help='Specify target team.')
parser.add_option('-r', '--reference', metavar='TEAM', default=reference,
                  help='Specify reference team.')
parser.add_option('-u', '--user', help='Specify user to check.')
parser.add_option('-b', '--both', action='store_true', default=False,
                  help='Print users who are in both teams.')
parser.add_option('-a', '--all', action='store_true', default=False,
                  help='Print all teams the user is in.')
parser.add_option('-m', '--markdown', action='store_true', default=False,
                  help='Print as Markdown.')
parser.add_option('-h', '--help', action='help', help='Print this help text.')
opts, args = parser.parse_args()


cachedir = "~/.cache/launchpadlib"
from launchpadlib.launchpad import Launchpad
launchpad = Launchpad.login_anonymously('Ubuntu IRC Cloaks Updater Script',
                'production', cachedir, version='devel')


def get_members(team):
    team = launchpad.people[team]
    teams = [team]
    teams.extend(team.sub_teams)
    members = {}
    for team in teams:
        for member in team.members:
            if not member.is_team:
                members[member.name] = member
    return members


def get_teams(team):
    team = launchpad.people[team]
    teams = {team.name: team}
    for sub_team in team.sub_teams:
        teams[sub_team.name] = sub_team
    return teams


def print_member(member):
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
        if not opts.user:
            output = u'{} - {}'.format(member.web_link, member.display_name)
        else:
            output = member.display_name
    else:
        output = u'link:{}[{}]'.format(member.web_link, member.display_name)

    # Check if they're active.
    if member.name.endswith('-deactivatedaccount') or gone:
        output += "'"
        if opts.markdown:
            output = "'" + output

    if nicks:
        output += u' ({})'.format(', '.join(nicks))

    if not opts.user:
        print(' * ' + output)
    else:
        if not opts.markdown:
            print(u'=== {} ==='.format(output))
            print(u'++ {} ++'.format(member.web_link))
        else:
            print(u'== {} =='.format(output))


def print_super_team(super_team):
    if not opts.markdown:
        print(u' * {} - {}'.format(super_team.web_link, super_team.display_name))
    else:
        print(u' * link:{}[{}]'.format(super_team.web_link, super_team.display_name))


if not opts.user:
    target_members = get_members(opts.target)
    reference_members = get_members(opts.reference)
    for member in sorted(target_members):
        if (not opts.both and member not in reference_members) or \
                (opts.both and member in reference_members):
            print_member(target_members[member])
else:
    try:
        member = launchpad.people[opts.user]
    except:
        sys.exit(1)

    if not member.is_team:
        target_teams = get_teams(opts.target)
        reference_teams = get_teams(opts.reference)
        print_member(member)

        super_teams = {}
        for super_team in member.super_teams:
            super_teams[super_team.name] = super_team

        team_scopes = {}
        for super_team in sorted(super_teams):
            if super_team in target_teams:
                team_scopes[0] = 'Target'
                print_super_team(super_teams[super_team])
            elif super_team in reference_teams:
                team_scopes[1] = 'Reference'
                print_super_team(super_teams[super_team])
            else:
                team_scopes[2] = 'Other'
                if opts.all:
                    print_super_team(super_teams[super_team])

        if not opts.markdown:
            print('\nTeam scopes: ' + (', '.join(list(team_scopes.values())) or 'None'))
        else:
            print('\n*Team scopes*: ' + (', '.join(list(team_scopes.values())) or 'None'))
