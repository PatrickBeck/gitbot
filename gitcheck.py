#! /usr/bin/env python
# -*- coding: utf-8 -*-

# File: gitcheck.py
# Version: 1.0
# Description: a few functions to check for updates in a git repo and return a log of the changes.
# Author: Patrick Beck (pbeck at yourse dot de) Copyright 2009
# License: GPL3

# git musst be installed to work with this script

# You have to set the variable giturl at the end of this script - then run it. It will clone the 
# current revision and creates the file git_revision. When anybody updates the git it will differ from 
# the content of the git_revision file and print all changes - and updates the git_revision file.

# You can test it manually when you edit the git_revision file to a number in the past

import sys
import os
import subprocess

class Gitcheck(object):

    def readfile(self, gitdir):
        try:
            file = open('git_revision', 'r') # file to save the revision number
            lastraw = file.read()
            file.close()
            last = lastraw.strip('\n') # delete the newline
            return last

        except:
            revision = self.getserverrevision(gitdir) # when no file exists, create a new one with the current revision from the server
            self.writefile(revision) # and write it
            print 'New git_revision file created - Nothing to do'
            sys.exit(0)

    def writefile(self, revision):
        try:
            file = open('git_revision', 'w') # overwrites the whole file when this function will be called
            file.write(revision)
            file.close()
        except:
            print 'No access rights? The file can\'t be written'
            
    def clone(self, giturl, gitdir):
        path = os.getcwd()
        if os.path.isdir(gitdir): # check if the dir exists
            pass # do nothing
        else:
            command = 'git', 'clone', giturl
            getclone = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # no terminaloutput of stdout
            clone = getclone.communicate() # interact with process
            if clone[1]: # it's None when no error comes up
                print 'Can\'t clone the repository - Error:', clone[1]
            else:
                print 'Repository cloned'

    def switchgitdir(self, gitdir):
        path = os.getcwd() # get path
        if os.path.isdir(gitdir): # exists the dir?
            os.chdir(gitdir) # change dir
        else:
            print 'Can\'t change the directory, directory not exists' 

    
    def switchbranch(self, gitdir, branch):
        self.switchgitdir(gitdir)
     	command = 'git', 'checkout', '-b', branch, 'origin/' + branch
#     	command = 'git', 'checkout', branch
	switchingbranch = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	branchswitched = switchingbranch.communicate()
	if branchswitched[0]: # None when no error comes up
            print 'Can\'t switch branch - Error:', branchswitched[0]
        else:
            print 'branch switched'
        self.switchback() # change back to the directory above - important to write the revision file
		
    def switchback(self):
        os.chdir('..') # change back to the directory above

    def fetch(self, gitdir):
        self.switchgitdir(gitdir)
        command = 'git', 'fetch'
        getfetch = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        fetch = getfetch.communicate()
        if fetch[1]: # None when no error comes up
            print 'Can\'t fetch the git repository - Error:', fetch[1]
        else:
            print 'origin repository updated'
        self.switchback() # change back to the directory above - important to write the revision file

    def getserverrevision(self, gitdir):
        self.switchgitdir(gitdir)
        command = 'git', 'log', '-1'
        getlog = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log = getlog.communicate()
        self.switchback() # change back to the directory above
        if log[1]: # error check
            print 'An error occured - Error:', log[1]
        else:
            revision = log[0][7:47] # get the stdout output (0) and extract the 40 character SHA1 Hash 
            return revision
                                                           
    def getlastrevision(self, gitdir):
        last = self.readfile(gitdir) 
        return last
            
    def getlog(self, last, server, gitdir):
        self.switchgitdir(gitdir)
        command = 'git', '--no-pager', 'log', last + '..' +  server, '--stat'
        getlog = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log = getlog.communicate()
        self.switchback()
        if log[1]: # error check
            print 'An Error occured - Error:', log[1]
        else:
            allupdates = [] # a empty list for all logs [[log1], [log2], ...]
            logmessage = log[0].split('commit') # split the big string into several log messages
            for log in logmessage[1:]: 
                entry = log.split('\n') # split the log message into his content
                update = [] # a empty list for one log [commit, author, date, logmessage, action]
                update.append(entry[0][1:]) # commit
                update.append(entry[1][8:]) # author
                update.append(entry[2][8:32]) # date
                update.append(entry[4][4:]) # logmessage
                update.append(entry[6:]) # action
                allupdates.append(update)
                self.writefile(str(server)) # write the server version to the file (for the next run of this script)
            allupdates.reverse()
            return allupdates

    def main(self, giturl, branch):
        giturlstrip = giturl.strip('/') # if the url has a slash at the end
        gitdir = giturlstrip.split('/')[-1].strip('.git') # get the dirname out of the giturl 
        self.clone(giturl, gitdir)
	self.switchbranch(gitdir, branch)
        self.fetch(gitdir)
        last = self.getlastrevision(gitdir)
        server = self.getserverrevision(gitdir)
        if last != server: # check if the repo has new commits
            
	    allupdates = self.getlog(last, server, gitdir) # get the output of the log
	    for i in allupdates:
                print '%s has updated to revision %s on %s. Comment: %s - Changed files => ' % (i[1], i[0], i[2], i[3]) # format the output
                for k in i[4]:
                    print k
                print ''
        else:
            print 'No updates'

if __name__ == '__main__':
    
    giturl = 'http://git.gitorious.org/epydial/epydial.git'
    branch = 'pyneo-1.32'
    check = Gitcheck()
    check.main(giturl, branch)
