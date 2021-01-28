#!/usr/bin/env python3
import os
import sys
from launchpadlib.launchpad import Launchpad

APP_NAME = 'ircmembers-roster'
CACHE_DIR = os.path.expanduser('~/.cache/launchpadlib')
SERVICE_ROOT = 'production'

launchpad = Launchpad.login_with(APP_NAME, SERVICE_ROOT, CACHE_DIR)
memberlist = launchpad.people["ubuntu-irc-members"].members_details

for member in memberlist:
	if (member.self_link.find("ubuntu-irc-council") == -1) and not(member.member.is_team):
		print(member.member.name, end=' ')
		try:
			print(member.member.preferred_email_address.email)
		except ValueError:
			print("<hidden>")
