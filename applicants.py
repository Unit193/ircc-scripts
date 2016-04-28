#!/usr/bin/env python
# this gets a group and iterates through it, and any subgroups to build a list of all members

#this bit is to tell it that it is totally cool to redirect unicode output to a file
#from http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=415968
import sys, codecs, getopt
if sys.stdout.encoding is None:
  sys.stdout = codecs.open("/dev/stdout", "w", 'utf-8')

cachedir = "~/.launchpadlib/cache"
from launchpadlib.launchpad import Launchpad, EDGE_SERVICE_ROOT
launchpad = Launchpad.login_with('People Lister', EDGE_SERVICE_ROOT, cachedir)

try:
  opts, args = getopt.getopt(sys.argv[1:],"hdp:",["parent="])
except getopt.GetoptError:
  print '-d, --devel set the parent team to ubuntu-core-devel-ops'
  print '-p, --parent <parent team>'
  sys.exit(2)

parent = "ubuntu-core-ops"
for opt, arg in opts:
    if opt == '-h':
        print '-d, --devel set the parent team to ubuntu-core-devel-ops'
        print '-p, --parent <parent team>'
        sys.exit()
    elif opt in ("-p", "--channel"):
        parent = arg
    elif opt in ("-d", "--devel"):
        parent = "ubuntu-core-devel-ops"

group = launchpad.people[parent]

#print group.display_name
memberships = group.members_details
allops={}
opsnicks={}


for sub_team in group.members:
  if sub_team.display_name[0]=='#':
    for membership in sub_team.members:
       allops[membership.web_link]=membership.display_name

#the sub_teams property of the top group seems to contain all nested groups, not just the direct members so we don't need to get recursive and worry about nesting loops
for sub_team in group.members:
  if sub_team.display_name[0]=='#' and sub_team.proposed_members:
    print '\n==', sub_team.display_name, '=='
    for membership in sub_team.proposed_members:
      try:
        for n in membership.irc_nicknames:
          if "freenode" in n.network.lower():
            opsnicks[membership.web_link]=membership.display_name
      except:
        continue
      if membership.web_link in allops: # Check to see if they're an OP in one of the other listed channels.
        if membership.web_link in opsnicks:
          print ' * link:%s[*%s*] - %s' % (membership.web_link, membership.display_name, n.nickname)
        else:
          print ' * link:%s[*%s*]' % (membership.web_link, membership.display_name)
      else:
        if membership.web_link in opsnicks:
          print ' * link:%s[%s] - %s' % (membership.web_link, membership.display_name, n.nickname)
        else:
          print ' * link:%s[%s]' % (membership.web_link, membership.display_name)
