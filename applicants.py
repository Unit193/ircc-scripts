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

group = launchpad.people['ubuntu-core-ops']#might be nice not to hard code this

#print group.display_name
memberships = group.members_details
allmemberships={}
#this is a dictionary of memberships, one per person, key is launchpad name (display name might not be unique). If we find a person in multiple groups the first one they joined is selected, thus the date when they first became an Ubuntu Member


for membership in memberships:
  if not membership.member.is_team:
#    print membership.member.display_name
    allmemberships[membership.member.name]=membership

#the sub_teams property of the top group seems to contain all nested groups, not just the direct members so we don't need to get recursive and worry about nesting loops
for sub_team in group.sub_teams:
  if sub_team.display_name[0]=='#':
    print '**** Team ****', sub_team.display_name
    for membership in sub_team.proposed_members:
       print membership.karma, membership.web_link, membership.display_name

#      #should only replace if it is an earlier membership
#      if allmemberships.has_key(membership.member.name):
#        if allmemberships[membership.member.name].date_joined > membership.date_joined:
#          allmemberships[membership.member.name]=membership
#      else:
#        allmemberships[membership.member.name]=membership

#with luck the allpeople dictionary now holds a unique list of all members
#print len(allmemberships)
#in theory at this point we should connect to google apps using the python API
#search column A of the spreadsheet for the launchpad name
#if found, move on
#otherwise insert a row in the right place and populate it with the lp name, real name, date joined launchpad and date made an Ubuntu Member

#for now just writing out in dirty old CSV format
#for membership in allmemberships:
#  person=allmemberships[membership].member
#  print '"' + person.name + '","' + person.display_name + '",' + person.date_created.date().isoformat() + ',' + allmemberships[membership].date_joined.date().isoformat() +','+ person.karma.__str__()
