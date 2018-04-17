#!/usr/bin/python

import os
import re
import subprocess
from subprocess import call
from datetime import datetime
from dateutil.parser import parse

class GitMsgObj(object):

	def __init__(self, commit, author, date, msg, merge):
		self.id = id # self generated 
		self.commit = commit.replace('\n', '')
		self.author = author.replace('\n', '')
		self.date = date.replace('\n', '')
		self.msg = msg.replace('\n', '')
		self.merge = merge

	def __repr__(self):
		# return '({},{},{})'.format(self.commit, self.author, self.msg)
		return self.commit + "	" + self.author + "	" + self.msg
		
	def __hash__(self):
		return hash((self.author, self.msg))

	def __eq__(self, other):
		try:
			return (self.msg, self.author) == (other.msg, other.author)
		except AttributeError:
			return NotImplemented


class GitWarrior():

	WMS_HOME = 'MyPro'
	TARGET_BRANCH = 'release_1.4.0'
	BRANCH_CREATION_DT = "2018-04-09T16:32:00+05:30"

	def __init__(self):
		pass

	def _update_branch(self, branch_name):
		FNULL = open(os.devnull, 'w')
		cmd = 'cd ./'+self.WMS_HOME+' && git checkout ' + branch_name + ' && git pull'
		call(cmd, stdout=FNULL, stderr=subprocess.STDOUT, shell=True)
		return True

	def _isStart(self, line):
		commit_pattern = '^commit*'
		if re.match(commit_pattern, line):
			return True
		else:
			return False

	def _isMergeMessage(self, line):
		merge_pattern = '^Merge*'
		if re.match(merge_pattern, line):
			return True
		else:
			return False

	def _get_commits(self, filename):
		allLines = [];
		commits = [];
		cmd = 'cd ./'+self.WMS_HOME+' && git log --after="'+ self.BRANCH_CREATION_DT +'" > ../' + filename
		call(cmd, shell=True)
		with open('./'+filename, 'r') as f:
			for line in f:
				allLines.append(line)
				
		commit_pattern = '^commit*'
		author_pattern = '^Author*'
		date_pattern = '^Date*'
		msg_pattern = '^\s\s\s\s*'
		merge_pattern = '^Merge*'

		i = 0
		while i < len(allLines):
			itm = {}
			if self._isStart(allLines[i]):
				if re.match(commit_pattern, allLines[i]):
					itm['commit'] = allLines[i][7:]

				next_line_num = i + 1
				if not self._isMergeMessage(allLines[next_line_num]):
					if re.match(author_pattern, allLines[i+1]):
						itm['author'] = allLines[i+1][8:].strip()

					if re.match(date_pattern, allLines[i+2]):
						datetime_object = parse(allLines[i+2][8:].strip())
						itm['date'] = datetime_object.isoformat()

					if re.match(msg_pattern, allLines[i+4]):
						itm['msg'] = allLines[i+4].strip()

					itm['merge'] = None
				else:
					if re.match(merge_pattern, allLines[i+1]):
						itm['merge']= allLines[i+1][8:].strip()

					if re.match(author_pattern, allLines[i+2]):
						itm['author'] = allLines[i+2][6:].strip()

					if re.match(date_pattern, allLines[i+3]):
						datetime_object = parse(allLines[i+3][8:].strip())
						itm['date'] = datetime_object.isoformat()

					if re.match(msg_pattern, allLines[i+5]):
						itm['msg'] = allLines[i+5].strip()

				commit_obj = GitMsgObj(itm['commit'], itm['author'], itm['date'], itm['msg'], itm['merge'])
				commits.append(commit_obj)
			i = i + 1

		return commits

	def run(self):
		print 'Updating Development.. '
		self._update_branch('Development')
		dev_commits = self._get_commits('dev.txt')
		print 'Updating ' + self.TARGET_BRANCH + ' ...'
		self._update_branch(self.TARGET_BRANCH)
		tb_commits = self._get_commits('tb.txt')

		devMinusTB = set(dev_commits) - set(tb_commits)
		TBMinusDev = set(tb_commits) - set(dev_commits)

		print "\n\n\n\n\n"
		
		if len(TBMinusDev) > 0:
			print "************************** Present in " + self.TARGET_BRANCH + " but missing in Development.. **************************"
			for msg in TBMinusDev:
				print msg

		print "\n\n\n\n\n"

		if len(devMinusTB) > 0:
			print "************************** Present in Development, but missing in " + self.TARGET_BRANCH + " .. **************************"
			for msg in devMinusTB:
				print msg

		# git log --all --grep=''
		# git log --grep=''

GitWarrior().run()