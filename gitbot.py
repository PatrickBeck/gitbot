#! /usr/bin/env python
# -*- coding: utf-8 -*- 

# File: gitbot.py
# Version: 1.0
# Description: Prints updates of git repositorys to irc
# Author: Patrick Beck (pbeck at yourse dot de) Copyright 2010
# License: GPL3

# gitbot.py uses the gitcheck.py library to generate the messages

# You need python-irclib, gitcheck.py library and git to run this script
# Then you have only to set the right git-repos and your parameters for bot, 
# channel, network and port at the end of this file

# This script is intended for run as a cronjob entry every few minutes / hours.

import irclib
import sys
import time
import gitcheck

class Gitbot(object):
    
    def connect(self, connection, event):
        for channel in channels:
            if irclib.is_channel(channel): # joins the channel when it exists
                connection.join(channel)

    def nicknameinuse(self, connection, event):
        connection.nick(connection.get_nickname() + "_") # when nickname in use add a _

    def sendmessage(self, connection, event):
            for channel in channels:
                for update in self.updates:
                    connection.privmsg(channel, update)
                    time.sleep(2) # kick protection :)
   
            sys.exit(0) # we have finished
    

    def main(self, botname, channel, network, port, username, repolist):
    
        git = gitcheck.Gitcheck()
        self.updates = git.main(repolist)
        if self.updates == []: # when no updates available
            print 'No updates'
            sys.exit(0)
        
        irc = irclib.IRC()
        try:
            c = irc.server().connect(network, port, botname, username=username)
        except irclib.ServerConnectionError, x:
            print x
            sys.exit(1)
        
        c.add_global_handler("welcome", self.connect)
        c.add_global_handler("join", self.sendmessage)
        c.add_global_handler('nicknameinuse', self.nicknameinuse)
        irc.process_forever()

if __name__ == '__main__':
    
    botname = '__pyneo'
    username = 'pyneo' # only alphanumerical characters
    channels = ['#pyneo.org'] # you can add as much channels as you like => channels = ['channel1','channel2','channel3']
    network = 'chat.freenode.net'
    port = 6667
    
    repolist = [ # a list with all controlled repositorys
    ['http://git.gitorious.org/epydial/epydial.git','master'],
    ['http://git.gitorious.org/epydial/epydial.git','pyneo-1.32'],
    ['http://git.gitorious.org/epydial/epydial-new.git','master'],
    ['http://git.pyneo.org/browse/cgit/paroli','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo','master'],
    ['http://git.pyneo.org/browse/cgit/python-ijon','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-zadthemes','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-gentoo','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-debian','master'],
    ['http://git.pyneo.org/browse/cgit/enlua','master'],
    ['http://git.pyneo.org/browse/cgit/python-aqbanking','master'],
    ['http://git.pyneo.org/browse/cgit/python-directfb','master'],
#    ['http://git.pyneo.org/browse/cgit/bwbasic','master'],
    ['http://git.pyneo.org/browse/cgit/robots','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-zadosk','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-zadwm','master'],
    ]

    bot = Gitbot()
    bot.main(botname, channels, network, port, username, repolist)
