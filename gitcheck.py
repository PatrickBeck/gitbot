#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: gitcheck.py
# Version: 1.2
# Description: a few functions to check for updates in a git repo and return a log of the changes.
# Author: Patrick Beck (pbeck at yourse dot de) Copyright 2011
# License: GPL3

# git musst be installed to work with this script

# You have to set the variable repolist at the end of this script - then run it. It will clone the 
# current revision and creates the file repos.csv. When anybody updates on of the git repositories it will differ from 
# the content of repos.csv file and print all changes. The main() function generates a log list as output. See the example
# at the end of this file. The main() function is written for the special job of returning updates of a repository.

# You can test it manually when you edit the repos.csv file to a SHA-1 number in the past

import sys
import os
import subprocess
import csv
import shutil

class Gitcheck(object):

    def readfile(self, repo, branch):
        '''Returns the sha, out of the *.csv file'''
        if os.path.isfile(self.data):
            file = csv.reader(open(self.data, 'r'), delimiter=',') # file to save the revision number
            for i in file:
                if repo == i[0] and branch == i[1]: # when repo and branch identically return the SHA-1
                    return i[2]

        revision = self.getserverrevision(repo, branch) # when no file exists, create a new one with the current revision from the server
        self.writefile(repo, branch, revision) # and write it
        print 'New repo in csv file added - %s on %s' % (repo, branch)
        
    def writefile(self, repo, branch, revision): # for new entrys only and if the new file are created
        '''Helper for changefile. Will write into file.'''
        file = open(self.data, 'a')
        file.write('%s,%s,%s\n' % (repo,branch,revision)) 
        file.close

    def changefile(self, repo, branch, revision): # to change the sha - update the file / rewrite it
        '''Updates or creates the *.csv file with repo,branch,sha. for last revision check.'''
        file = open(self.data, 'r')
        fileContent = []
        while 1:
            line = file.readline()
            if '%s,%s' % (repo, branch) in line: # when repo,branch found update the revision
                fileContent.append('%s,%s,%s\n' % (repo, branch, revision))
            else:
                fileContent.append(line) # other should be added directly
            if not line: # end of lines in csv file
                break
        file = open(self.data, 'w')
        for i in fileContent:
            file.write(i)
        file.close
            
    def cleanFile(self, repolist):
        '''Cleans up the *.csv file, when repositorys are removed out of the repolist.'''
        file = open(self.data, 'r')
        content = file.readlines() # get the whole content of repos.csv
        if repolist == []: # the part for deleting all content (csv file and old dirs), when no repo is set.
            for i in content:
                gitdir = self.getDir(i.split(',')[0])
                self.cleanDir(gitdir) # remove the dirs which are listed in the csv file
            os.remove(self.data) # delete csv file
            return

        new_list = [] 
        for i in content:
            for repo in repolist:
                if repo[0] + ',' + repo[1] in i: # when repo of repolist is in csv file
                    new_list.append(i) # add it to the list
        
        file = open(self.data, 'w')
        for i in new_list:
            i = i.split(',') # split the string into - repo, branch and sha
            file.write('%s,%s,%s' % (i[0],i[1],i[2])) # add only the current repos of repolist in csv file - delete the other
        file.close
        
        for i in content:
            if i not in new_list:
                i = i.split(',') # get the repo, branch and sha out of the string
                gitdir = self.getDir(i[0])
                for entry in new_list:
                    if i[0] not in entry.split(',')[0]: # test if a repo with more than one branch is added - don't delete it
                        self.cleanDir(gitdir) # when repo list clear, delete the directorys to the entrys
                    else:
                        print 'Repo - %s/%s - deleted' % (i[0],i[1])
        
                
    def cleanDir(self, repo):
        '''Cleans up the directory, when some repositorys are removed out of the repolist.'''
        gitdir = self.getDir(repo)
        if os.path.isdir(gitdir):
            shutil.rmtree(gitdir) # delete the directory of the repository
            print 'Directory and Repo - %s - deleted' % (gitdir)

            
    def clone(self, repo):
        '''Creates a new local repository out of the remote git url'''
        gitdir = self.getDir(repo)
        if os.path.isdir(gitdir): # check if the dir exists
            pass # do nothing
        else:
            command = 'git', 'clone', repo
            getclone = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # no terminaloutput of stdout
            clone = getclone.communicate() # interact with process
            if clone[1]: # it's None when no error comes up
                print 'Can\'t clone the repository - Error:', clone[1]
                return False # not possible to clone repo
            else:
                print 'Repository %s cloned' % (repo)

    def fetch(self, repo):
        '''Downloads updates of a remote git repository (will be not merged)'''
        self.switchgitdir(repo)
        command = 'git', 'fetch'
        getfetch = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        fetch = getfetch.communicate()
        self.switchgitdir(repo) # change back to the directory above - important to write the csv file
        if fetch[1]: # None when no error comes up
            print 'Can\'t fetch the git repository - Error:', fetch[1]
            return False # not possible to update the repo
        else:
            print 'origin repository for %s updated' % (repo)


    def switchgitdir(self, repo):
        '''Switch in git repo dir and back, when already inside'''
        repodir = self.getDir(repo)
        if os.path.isdir(repodir): # exists the dir?
            os.chdir(repodir) # change dir # change dir
            print 'Switch into %s' % (repodir)
        else:
            print 'Switch back to %s' % (self.absolute)
            os.chdir(self.absolute) # change back to main directory

    
    def switchbranch(self, branch):
        '''Switch in branch - you have to select first the gitdir with switchgitdir()'''
        command = 'git', 'checkout', branch
        switchingbranch = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        branchswitched = switchingbranch.communicate()
        if branchswitched[0]: # None when no error comes up
            print '%s - Branch to %s switched' % (branchswitched[0], branch)
        else:
            print 'branch to %s switched' % (branch)
		
    def getserverrevision(self, repo, branch):
        '''Get the current git revision out of repo and branch, selectable with switchgitdir and switchbranch'''
        self.switchgitdir(repo)
        self.switchbranch(branch)
        command = 'git', 'log', 'origin', '-1'
        getlog = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log = getlog.communicate()
        self.switchgitdir(repo) # change back to the directory above
        if log[1]: # error check
            print 'An error occured - Error:', log[1]
        else:
            revision = log[0][7:47] # get the stdout output (0) and extract the 40 character SHA1 Hash 
            return revision
                                                           
    def getlastrevision(self, repo, branch):
        '''Get the last saved revision out of a *.csv file, with repo and branch'''
        revision = self.readfile(repo, branch) 
        return revision
     
    def formatlog(self, log, repo, branch):
        '''Format the output of git log'''
        allmessages = []
        logmessage = log[0].split('commit') # split the big string into several log messages
        for log in logmessage[1:]:
            entry = log.split('\n') # split the log message into his content
            message = [] # a empty list for one log [repo, branch, author, date, commit, logmessage, action]
            message.append(self.getDir(repo)) # repo
            message.append(branch) # branch
            message.append(entry[1][8:].split(' <')[0]) # author (get only the name without email)
            message.append(entry[2][8:32]) # date
            message.append(entry[0][1:-30] + '...') # commit (only the first ten characters)
            message.append(entry[4][4:]) # logmessage
#           update.append(entry[6:]) # action # to much output
            allmessages.append(message)
            print allmessages
        return allmessages
       


    def getDir(self, giturl):
        '''Returns the directory name out of the git adress in web'''
        gitdir = giturl.strip('/').split('/')[-1].replace('.git', '')
        return gitdir

    def absolutePath(self):
        '''Returns the absolute Path to the main directory of this file'''
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

    def getlog4sha(self, sha, repo, branch):
        self.switchgitdir(repo)
        self.switchbranch(branch)
        allupdates = [] # a empty list for all logs [[log1], [log2], ...]
        
        if sha == None:
            pass
        else:

            if '..' in sha: # range of logs
                sha = sha.split('..')
                command = 'git', '--no-pager', 'log', sha[0] + '..' +  sha[1], '--stat'
            else:
                command = 'git', '--no-pager', 'log', '-1', sha, '--stat'
            print command
            getlog = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            log = getlog.communicate()
            if log[1]: # error check
                print 'An Error occured - Error:', log[1]
            else:
                allupdates = self.formatlog(log, repo, branch)
        
        self.switchgitdir(repo)
        allupdates.reverse()
        return allupdates

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
                allupdates = self.formatlog(log, repo, branch)
        
        self.switchgitdir(repo)
        self.changefile(repo, branch, server) # write the server version to the file (for the next run of this script)
        allupdates.reverse()
        return allupdates

    def getSHALog(self, repolist, sha):
        updates = []
        for i in repolist:
            if self.clone(i[0]) or self.fetch(i[0]) == False: # clone the repo it not clones, update the origin remote
                continue # when the repo is not reachable, skip the defect one
            
            log = self.getlog4sha(sha[0], i[0], i[1]) # get the output of the log
            
            for i in log[0:5]: #limit to 5 logs per request. 
                allupdates = '[%s / %s] %s at %s on %s [%s]' % (i[0], i[1], i[2], i[3], i[4], i[5]) #, i[6]) # to much output
                updates.append(allupdates)
        return updates

    def main(self):
        updates = []
        for i in self.repolist:
            if self.clone(i[0]) or self.fetch(i[0]) == False: # clone the repo it not clones, update the origin remote
                continue # when the repo is not reachable, skip the defect one
            
            last = self.getlastrevision(i[0],i[1]) # get the last revision out of the csv file
            server = self.getserverrevision(i[0],i[1]) # get the current revision from the server
            print last, server 
            if last != server: # check if the repo has new commits
                up = self.getlog(last, server, i[0], i[1]) # get the output of the log
                print up
                for i in up:
                    allupdates = '[%s / %s] %s at %s on %s [%s]' % (i[0], i[1], i[2], i[3], i[4], i[5]) #, i[6]) # to much output
                    updates.append(allupdates)
        return updates
        
    def __init__(self, repolist):
        
        self.repolist = repolist
        self.absolute = self.absolutePath() # get into the right directory
        self.data = 'repos.csv' # file for saving the data
        
        os.chdir(self.absolute) # get into the right directory
        
        if os.path.isfile(self.data): # have to be called after the new written csv file
           self.cleanFile(repolist) # clean the directory or csv file
 
if __name__ == '__main__': # function will only be called when you start the script directly
    
    repolist = [ # a list with all controlled repositorys
#    ['http://git.gitorious.org/epydial/epydial.git','master'],
#    ['http://git.gitorious.org/epydial/epydial.git','pyneo-1.32'],
#    ['http://git.gitorious.org/epydial/epydial-new.git','master'],
#    ['http://git.pyneo.org/browse/cgit/paroli','master'],
#    ['http://git.pyneo.org/browse/cgit/pyneo-pyneod','master'],
#    ['http://git.pyneo.org/browse/cgit/pyneo-pybankd','master'],
#    ['http://git.pyneo.org/browse/cgit/pyneo-pyrssd','master'],
#    ['http://git.pyneo.org/browse/cgit/pyneo-pyaudiod','master'],
#    ['http://git.pyneo.org/browse/cgit/pyneo-zad','master'],
#    ['http://git.pyneo.org/browse/cgit/python-pyneo','master'],
#    ['http://git.pyneo.org/browse/cgit/pyneo-resolvconf','master'],
#    ['http://git.pyneo.org/browse/cgit/gsm0710muxd','master'],
#    ['http://git.pyneo.org/browse/cgit/gllin','master'],
#    ['http://git.pyneo.org/browse/cgit/pyneo-pygsmd','master'],
#    ['http://git.pyneo.org/browse/cgit/pyneo','master'],
#    ['http://git.pyneo.org/browse/cgit/python-ijon','master'],
#    ['http://git.pyneo.org/browse/cgit/pyneo-zadthemes','master'],
#    ['http://git.pyneo.org/browse/cgit/pyneo-gentoo','master'],
#    ['http://git.pyneo.org/browse/cgit/pyneo-debian','master'],
#    ['http://git.pyneo.org/browse/cgit/enlua','master'],
#    ['http://git.pyneo.org/browse/cgit/python-aqbanking','master'],
#    ['http://git.pyneo.org/browse/cgit/python-directfb','master'],
#    ['http://git.pyneo.org/browse/cgit/bwbasic','master'],
#    ['http://git.pyneo.org/browse/cgit/robots','master'],
#    ['http://git.pyneo.org/browse/cgit/pyneo-zadosk','master'],
#    ['http://git.pyneo.org/browse/cgit/pyneo-zadwm','master'],
     ['https://git.gitorious.org/ecdial/ecdial.git','master'],
    ]
 
    
    check = Gitcheck()
    updates = check.main(repolist)
    if updates == []:
        print 'No Updates'
    else:
        for i in updates:
            print i
