#! /usr/bin/env python
# -*- coding: utf-8 -*-

# File: gitcheck.py
# Version: 0.5
# Description: a few functions to check for updates in a git repo and return a log of the changes.
# Author: Patrick Beck (pbeck at yourse dot de) Copyright 2010
# License: GPL3

# git musst be installed to work with this script

# You have to set the variable giturl and branch at the end of this script - then run it. It will clone the 
# current revision and creates the file git_revision. When anybody updates the git it will differ from 
# the content of the git_revision file and print all changes - and updates the git_revision file.

# You can test it manually when you edit the git_revision file to a number in the past

import sys
import os
import subprocess
import csv

class Gitcheck(object):

    def readfile(self, repo, branch):
        if os.path.isfile('repos.csv'):
            file = csv.reader(open('repos.csv', 'r'), delimiter=',') # file to save the revision number
            print file
            for i in file:
                if repo == i[0] and branch == i[1]:
                    return i[2]
#                else:
#                    revision = self.getserverrevision(repo, branch) # when no file exists, create a new one with the current revision from the server
#                    self.writefile(repo, branch, revision) # and write it
#                    print 'New repo in csv file added - %s on %s' % (repo, branch)
        
        else:
            revision = self.getserverrevision(repo, branch) # when no file exists, create a new one with the current revision from the server
            self.writefile(repo, branch, revision) # and write it
            print 'New repo in csv file added - %s on %s' % (repo, branch)
        
    def writefile(self, repo, branch, revision):
        file = open('repos.csv', 'a')
        file.write('%s,%s,%s\n' % (repo,branch,revision)) 
        file.close

    def clone(self, repo):
        path = os.getcwd()
        gitdir = self.getDir(repo)
        if os.path.isdir(gitdir): # check if the dir exists
            pass # do nothing
        else:
            command = 'git', 'clone', repo
            getclone = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # no terminaloutput of stdout
            clone = getclone.communicate() # interact with process
            if clone[1]: # it's None when no error comes up
                print 'Can\'t clone the repository - Error:', clone[1]
            else:
                print 'Repository %s cloned' % (repo)

    def switchgitdir(self, repo):
        path = os.getcwd() # get path
        repodir = self.getDir(repo)
        if os.path.isdir(repodir): # exists the dir?
            os.chdir(repodir) # change dir
        else:
            print 'Can\'t change the directory to %s, directory not exists' % (repo) 

    
    def switchbranch(self, branch):
        command = 'git', 'checkout', '-b', branch, 'origin/' + branch
        switchingbranch = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        branchswitched = switchingbranch.communicate()
        if branchswitched[0]: # None when no error comes up
            print 'Can\'t switch branch - Error:', branchswitched[0]
        else:
            print 'branch to %s switched' % (branch)
		
    def switchback(self):
        os.chdir('..') # change back to the directory above

#    def fetch(self, gitdir):
#        self.switchgitdir(gitdir)
#        command = 'git', 'fetch'
#        getfetch = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#        fetch = getfetch.communicate()
#        if fetch[1]: # None when no error comes up
#            print 'Can\'t fetch the git repository - Error:', fetch[1]
#        else:
#            print 'origin repository updated'
#        self.switchback() # change back to the directory above - important to write the revision file

    def getserverrevision(self, repo, branch):
        self.switchgitdir(repo)
        self.switchbranch(branch)
        command = 'git', 'log', '-1'
        getlog = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log = getlog.communicate()
        self.switchback() # change back to the directory above
        if log[1]: # error check
            print 'An error occured - Error:', log[1]
        else:
            revision = log[0][7:47] # get the stdout output (0) and extract the 40 character SHA1 Hash 
            return revision
                                                           
    def getlastrevision(self, repo, branch):
        revision = self.readfile(repo, branch) 
        return revision
            
    def getlog(self, last, server, repo, branch):
        self.switchgitdir(repo)
        self.switchbranch(branch)
        allupdates = [] # a empty list for all logs [[log1], [log2], ...]
        if last == None:
            pass
        else:
            command = 'git', '--no-pager', 'log', last + '..' +  server, '--stat'
            getlog = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            log = getlog.communicate()
            if log[1]: # error check
                print 'An Error occured - Error:', log[1]
            else:
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
                    self.writefile(repo, branch, revision) # write the server version to the file (for the next run of this script)
        self.switchback()
        allupdates.reverse()
        return allupdates

    def getDir(self, giturl):
        gitdir = giturl.strip('/').split('/')[-1].strip('.git')
        return gitdir

    def main(self, repolist):
        updates = []
        for i in repolist:
            self.clone(i[0])
            last = self.getlastrevision(i[0],i[1])
            server = self.getserverrevision(i[0],i[1])

            if last != server: # check if the repo has new commits
                allupdates = self.getlog(last, server, i[0], i[1]) # get the output of the log
                updates.append(allupdates)
        return updates
                
if __name__ == '__main__':
    
    repolist = [
    ['http://git.gitorious.org/epydial/epydial.git','master'],
    ['http://git.gitorious.org/epydial/epydial.git','pyneo-1.32'],
    ]
    check = Gitcheck()
    updates = check.main(repolist)
    if updates == []:
        print 'No Updates'
    else:
        print updates
