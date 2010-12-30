#! /usr/bin/env python
# -*- coding: utf-8 -*-

# File: gitcheck.py
# Version: 0.1
# Description: a few functions to check for updates in a git repo and return a log of the changes.
# Author: Patrick Beck (pbeck at yourse dot de) Copyright 2010
# License: GPL3

# git musst be installed to work with this script

# You have to set the variable repolist at the end of this script - then run it. It will clone the 
# current revision and creates the file repos.csv. When anybody updates on of the git repositories it will differ from 
# the content of repos.csv file and print all changes. The main() function generates a log list as output. See the example
# at the end of this file. The main() function is written for the special job of returning updates of a repository.

# You can test it manually when you edit the repos.csv file to a number in the past

import sys
import os
import subprocess
import csv
import shutil

class Gitcheck(object):

    def readfile(self, repo, branch):
        if os.path.isfile(self.data):
            file = csv.reader(open(self.data, 'r'), delimiter=',') # file to save the revision number
            for i in file:
                if repo == i[0] and branch == i[1]:
                    return i[2]

            revision = self.getserverrevision(repo, branch) # when no file exists, create a new one with the current revision from the server
            self.writefile(repo, branch, revision) # and write it
            print 'New repo in csv file added - %s on %s' % (repo, branch)
        
        else:
            revision = self.getserverrevision(repo, branch) # when no file exists, create a new one with the current revision from the server
            self.writefile(repo, branch, revision) # and write it
            print 'New repo in csv file added - %s on %s' % (repo, branch)
        
    def writefile(self, repo, branch, revision): # for new entrys only and if the new file are created
        file = open(self.data, 'a')
        file.write('%s,%s,%s\n' % (repo,branch,revision)) 
        file.close

    def changefile(self, repo, branch, revision): # to change the sha - update the file
        file = open(self.data, 'r')
        fileContent = []
        while 1:
            line = file.readline()
            if '%s,%s' % (repo, branch) in line:
                fileContent.append('%s,%s,%s\n' % (repo, branch, revision))
            else:
                fileContent.append(line)
            if not line:
                break
        file = open(self.data, 'w')
        for i in fileContent:
            file.write(i)
        file.close
            

    def cleanFile(self, repolist):
        file = open(self.data, 'r')
        content = file.readlines() # get the whole content of repos.csv
        new_list = [] 
        for i in content:
            for repo in repolist:
                if repo[0] + ',' + repo[1] in i: # when repo of repolist is in repos.csv
                    new_list.append(i) # add it to the list
        
        file = open(self.data, 'w')
        for i in new_list:
            i = i.split(',') # split the string into - repo, branch and sha
            file.write('%s,%s,%s' % (i[0],i[1],i[2])) # add only the current repos of repolist in repos.csv - delete the other
        file.close

    def cleanDir(self, repo):
        gitdir = self.getDir(repo)
        if os.path.isdir(gitdir)
            shutil.rmtree(gitdir)
            print 'Repo - %s - deleted' % (gitdir)

            
    def clone(self, repo):
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
        repodir = self.getDir(repo)
        if os.path.isdir(repodir): # exists the dir?
            os.chdir(repodir) # change dir
        else:
            print 'Can\'t change the directory to %s, directory not exists' % (repo) 

    
    def switchbranch(self, branch):
#        command = 'git', 'checkout', '-b', branch, 'origin/' + branch
        command = 'git', 'checkout', branch
        switchingbranch = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        branchswitched = switchingbranch.communicate()
        if branchswitched[0]: # None when no error comes up
            print 'Can\'t switch branch - Error:', branchswitched[0]
        else:
            print 'branch to %s switched' % (branch)
		
    def switchback(self):
        os.chdir('..') # change back to the directory above


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
                    update = [] # a empty list for one log [repo, branch, author, date, commit, logmessage, action]
                    update.append(self.getDir(repo)) # repo
                    update.append(branch) # branch
                    update.append(entry[1][8:]) # author
                    update.append(entry[2][8:32]) # date
                    update.append(entry[0][1:]) # commit
                    update.append(entry[4][4:]) # logmessage
#                    print entry[6:][0]#.replace('\n','')#, entry[6:][1].replace('\n','')
                    update.append(entry[6:])#[0] + entry[6:][1]) # action
                    allupdates.append(update)
        self.switchback()
#        self.changefile(repo, branch, server) # write the server version to the file (for the next run of this script)
        allupdates.reverse()
        return allupdates

    def getDir(self, giturl):
        gitdir = giturl.strip('/').split('/')[-1].replace('.git', '')
        return gitdir

    def absolutePath(self):
        workingDir = os.getcwd() # get the current directory
        appName = sys.argv[0].split('/')[-1] # get the application name
        pathToFile = sys.argv[0].rstrip(appName) # extract the path from the current dir to the app - and exclude the application name

        if pathToFile == '': # when application is in the same dir
            scriptDir = '%s/' % (workingDir)
        elif pathToFile[0] == '/': # to differentiate between absolute and relative path
            scriptDir = pathToFile # absolute path
        else:
            scriptDir = '%s/%s' % (workingDir, pathToFile) # create the absolute path out of the relative one
        return scriptDir

    def main(self, repolist):
        os.chdir(self.absolutePath()) # get into the right directory
        self.data = 'repos.csv' # saves the repo + branch + the last sha
        updates = []
        for i in repolist:
            self.clone(i[0])
            last = self.getlastrevision(i[0],i[1])
            server = self.getserverrevision(i[0],i[1])

            if last != server: # check if the repo has new commits
                up = self.getlog(last, server, i[0], i[1]) # get the output of the log
                for i in up:
                    allupdates = '[%s / %s] %s at %s on %s. Comment: %s Changes: %s' % (i[0], i[1], i[2], i[3], i[4], i[5], i[6])
                    updates.append(allupdates)
        self.cleanFile(repolist)
        return updates
                
if __name__ == '__main__':
    
    repolist = [
#    ['http://git.gitorious.org/epydial/epydial.git','master'],
    ['http://git.gitorious.org/epydial/epydial.git','pyneo-1.32'],
#    ['http://git.gitorious.org/epydial/epydial-new.git','master'],
#    ['http://git.pyneo.org/browse/cgit/paroli','master'],
#    ['http://git.pyneo.org/browse/cgit/pyneo','master'],
#    ['http://git.pyneo.org/browse/cgit/pyneo-zadosk','master'],
#    ['http://git.pyneo.org/browse/cgit/pyneo-zadwm','master'],
    ]
    check = Gitcheck()
    updates = check.main(repolist)
    if updates == []:
        print 'No Updates'
    else:
        for i in updates:
            print i
