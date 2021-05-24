#!/usr/bin/env python3
import sys
import getopt
from launchpadlib.launchpad import Launchpad

try:
    opts, args = getopt.getopt(sys.argv[1:],"hc:",["channel="])
except getopt.GetoptError:
        print('-c, --channel <channel name>')
        print('When specifying a channel, omit the hash.')
        sys.exit(2)

channel = ""
for opt, arg in opts:
    if opt == '-h':
        print('-c, --channel <channel name>')
        print('When specifying a channel, omit the hash.')
        sys.exit()
    elif opt in ("-c", "--channel"):
        channel = arg

_get_team_members_done = [] # Cache of already fetched Launchpad teams
def get_team_members(launchpad, team):
    '''Get all members of a team and all sub-teams.
    Returns a set of Person names
    '''

    if team in _get_team_members_done: # Don't fetch team members multiple times
        return set()

    _get_team_members_done.append(team)
    try: team = launchpad.people[team]
    except KeyError:
        print("The team for '" + channel + "' does not exist on Launchpad.")
        sys.exit(2)
    members = set()

    for member in team.members:
        if not member.is_team:
            for irc_id in member.irc_nicknames:
                network = irc_id.network.lower()
                if any(map(network.__contains__, ['freenode', 'ubuntu'])):
                    members.add(irc_id.nickname)

    return members

launchpad = Launchpad.login_anonymously('Ubuntu IRC',
    service_root='production', version='1.0')

members = get_team_members(launchpad, u'irc-' + channel + '-ops')

ops = "flags #" + channel + " " + (u'\nflags #%s ' % channel).join(members).replace('\n',' +Aiortv\n') + " +Aiortv"

# Setting up some default OPs
print("flags #" + channel + " UbuntuIrcCouncil +Afiortv")
print("flags #" + channel + " *!*@freenode/staff/* +Aiortv")
print("flags #" + channel + " ubottu +Aiotv")
print(ops)
