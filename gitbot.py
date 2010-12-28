#! /usr/bin/env python
# -*- coding: utf-8 -*- 

# File: gitbot.py
# Version: 0.5
# Description: Prints updates in the svn and git repository to irc
# Author: Patrick Beck (pbeck at yourse dot de) Copyright 2009
# License: GPL3

# gitbot.py uses the gitcheck.py library to generate the messages

# You need python-irclib, gitcheck.py library and git to run this script
# Then you have only to set the right git-repos and your parameters for bot, 
# channel, network and port.

# This script is intended for run as a cronjob entry every few minutes / hours.

import irclib
import sys
import time
import gitcheck

class Gitbot(object):
    
    def connect(self, connection, event):
        if irclib.is_channel(channel): # joins the channel when it exists
            connection.join(channel)

    def nicknameinuse(self, connection, event):
        connection.nick(connection.get_nickname() + "_") # when nickname in use add a _

    def sendmessage(self, connection, event):
            for update in self.updates:
                connection.privmsg(channel, update)
                time.sleep(2) # kick protection :)
   
            sys.exit(0) # we have finished
    

    def main(self, botname, channel, network, port, repolist):
    
        git = gitcheck.Gitcheck()
        self.updates = git.main(repolist)
        if self.updates == []: # when no updates available
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
    channel = '#pyneo-test'
    network = 'chat.freenode.net'
    port = 6667
    
    repolist = [
    ['http://git.gitorious.org/epydial/epydial.git','master'],
    ['http://git.gitorious.org/epydial/epydial.git','pyneo-1.32'],
    ['http://git.pyneo.org/browse/cgit/paroli','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-zadosk','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-zadwm','master'],
    ]

    bot = Gitbot()
    bot.main(botname, channel, network, port, repolist)
