#!/usr/bin/python
# -*- Encoding: UTF-8 -*-
from launchpadlib.launchpad import Launchpad

_get_team_members_done = [] # Cache of already fetched Launchpad teams
def get_team_members(lp, team):
    '''Get all members of a team and all sub-teams.
    Returns a set of Person names
    '''

    if team in _get_team_members_done: # Don't fetch team members multiple times
        return set()

    _get_team_members_done.append(team)
    team = lp.people[team]
    members = set()

    for member in team.members:
        if not member.is_team:
            members.add(member.name)
        else: # Recurs into sub-teams
            members.update(get_team_members(lp, member.name))

    return members


lp = Launchpad.login_anonymously('Ubuntu IRC Cloaks Updater Script',
    service_root='production', version='1.0')

cloaks = get_team_members(lp, u'ubuntu-irc-cloaks')
_get_team_members_done = [] # Clear the cache of retrieved teams
members = get_team_members(lp, u'ubuntumembers')
#members=set()
#cloaks=("alanbell",)

# The members printed are those who are no longer members of ~ubuntumembers
for p in cloaks:
    if p not in members:
        print u'\n\n' + 'http://launchpad.net/~'+ p
        person=lp.people[p]
        #print dir(person)
        for nick in person.irc_nicknames:
            print nick.network, nick.nickname
