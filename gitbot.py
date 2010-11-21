#! /usr/bin/env python
# -*- coding: utf-8 -*- 

# File: svngitbot.py
# Version: 1.1
# Description: Prints updates in the svn and git repository to irc
# Author: Patrick Beck (pbeck at yourse dot de) Copyright 2009
# License: GPL3

# svngitbot.py uses the svncheck.py and gitcheck.py library to generate the messages

# You need python-irclib, svn and my svncheck.py and gitcheck.py library to run this script
# Then you have only to set the right svnurl / giturl and your parameters for bot, 
# channel, network and port.

# This script is intended for run as a cronjob entry every few minutes / hours
# On the first run you have to start the script twice, because it checksout the svn repo first 
# and then clones the git repo.

import irclib
import sys
import time
import svncheck
import gitcheck

class SvnGitbot(object):
    
    def connect(self, connection, event):
        if irclib.is_channel(channel): # joins the channel when it exists
            connection.join(channel)

    def nicknameinuse(self, connection, event):
        connection.nick(connection.get_nickname() + "_") # when nickname in use add a _

    def sendmessage(self, connection, event):
            if self.allupdatesgit != None: # git updates
                for i in self.allupdatesgit:
                    connection.privmsg(channel, '%s: %s on %s. Comment: %s' % (self.gitdir, i[1], i[2], i[3])) # format the output
                    time.sleep(2) # kick protection :)
   
            sys.exit(0) # we have finished
    

    def main(self, botname, channel, network, port, giturl, branch):
    
        git = gitcheck.Gitcheck()
        self.giturlstrip = giturl.strip('/') # if the url has a slash at the end
        self.gitdir = self.giturlstrip.split('/')[-1].strip('.git') # get the dirname out of the giturl 
        git.clone(giturl, self.gitdir) # clone the repo if it not exists
        git.switchbranch(self.gitdir, branch)
	git.fetch(self.gitdir) # update the local origin repo
        lastgit = git.getlastrevision(self.gitdir) # get the last version
        servergit = git.getserverrevision(self.gitdir) # get the current version of the repo

        if lastgit != servergit:
            self.allupdatesgit = git.getlog(lastgit, servergit, self.gitdir)
        else:
            self.allupdatesgit = None
            print 'No git updates'

        if self.allupdatesgit == None: 
            sys.exit(0)
        
        irc = irclib.IRC()
        try:
            c = irc.server().connect(network, port, botname)
        except irclib.ServerConnectionError, x:
            print x
            sys.exit(1)
        
        c.add_global_handler("welcome", self.connect)
        c.add_global_handler("join", self.sendmessage)
        c.add_global_handler('nicknameinuse', self.nicknameinuse)
        irc.process_forever()

if __name__ == '__main__':
    
    botname = 'pyneo-bot'
    channel = '#pyneo.org'
    network = 'chat.freenode.net'
    port = 6667
    giturl = 'http://git.gitorious.org/epydial/epydial.git'
    branch = 'pyneo-1.32'
    bot = SvnGitbot()
    bot.main(botname, channel, network, port, giturl, branch)
