#!/usr/bin/env python
# this gets a group and iterates through it, and any subgroups to build a list of all members

#this bit is to tell it that it is totally cool to redirect unicode output to a file
#from http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=415968
import sys, codecs
if sys.stdout.encoding is None:
  sys.stdout = codecs.open("/dev/stdout", "w", 'utf-8')

cachedir = "~/.launchpadlib/cache"
from launchpadlib.launchpad import Launchpad, EDGE_SERVICE_ROOT
launchpad = Launchpad.login_with('People Lister', EDGE_SERVICE_ROOT, cachedir)

group = launchpad.people['ubuntu-ops']#might be nice not to hard code this

#print group.display_name
memberships = group.members_details
allops={}

for sub_team in group.sub_teams:
  if sub_team.display_name[0]=='#':
    print '**** Team ****', sub_team.display_name
    for membership in sub_team.members:
       allops[membership.web_link]=membership.display_name
       print membership.web_link, membership.display_name

