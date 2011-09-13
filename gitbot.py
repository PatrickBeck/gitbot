#! /usr/bin/env python
# -*- coding: utf-8 -*- 

# File: gitbot.py
# Version: 1.2.2
# Description: Prints updates of git repositorys to irc
# Author: Patrick Beck (pbeck at yourse dot de) Copyright 2011
# License: GPL3

# gitbot.py uses the gitcheck.py library to generate the messages

# You need python-irclib, gitcheck.py library and git to run this script
# Then you have only to set the right git-repos and your parameters for bot, 
# channel, network and port at the end of this file

# This script is intended for run as a background process the whole time - when you only want a script use the Version 1.0.1.

import sys
import time
import sqlite3
import irclib
import gitcheck

class Gitbot(object):
    
    def connect(self, connection, event):
        for channel in channels:
            if irclib.is_channel(channel): # joins the channel when it exists
                connection.join(channel)

    def pong(self, connection, event):
        connection.pong(event.target())

    def nicknameinuse(self, connection, event):
        connection.nick(connection.get_nickname() + "_") # when nickname in use add a _

    def learnfact(self, buzzword, description, connection, event):
        self.cur.execute('SELECT buzzword, description FROM facts')
        for row in self.cur:
            if row[0] == buzzword: 
                content = (description, buzzword)
                add = 'UPDATE facts SET description = ? where buzzword = ?'
                self.cur.execute(add, content)
                self.con.commit()
                self.sendChannel('Factoid %s updated' % (buzzword), connection, event)
                return

        content = (buzzword, description)
        add = 'INSERT INTO facts VALUES (?, ?)'
        self.cur.execute(add, content)
        self.con.commit()
        self.sendChannel('Factoid %s saved' % (buzzword), connection, event)

    def deletefact(self, buzzword, connection, event):
        self.cur.execute('SELECT buzzword, description FROM facts')
        for row in self.cur:
            if row[0] == buzzword:
                content = (row[0], row[1])
                delete = 'DELETE FROM facts where buzzword = ? and description = ?'
                self.cur.execute(delete, content)
                self.con.commit()
                self.sendChannel('Factoid %s deleted' % (buzzword), connection, event)

    def outputfact(self, buzzword, connection, event, user=None):
        self.cur.execute('SELECT buzzword, description FROM facts')
        for row in self.cur:
            if row[0] == buzzword: 
                if user == None:
                    text ='%s %s' % (row[0], row[1])
                else:
                    text = '%s, %s %s' % (user, row[0], row[1])
                self.sendChannel(text, connection, event)
   
    def listfacts(self, connection, event):
        self.cur.execute('SELECT buzzword FROM facts')
        words = []
        for row in self.cur:
            words.append(row[0])
        text = 'Saved facts - '+', '.join(words)
        self.sendChannel(text, connection, event)
            

    def sendChannel(self, text, connection, event):
        connection.privmsg(event.target(), text)

    def pubmsg(self, connection, event):
        msg = event.arguments()[0]
        
        if msg.startswith('!facts'):
            self.listfacts(connection, event)
        
        elif msg.startswith('!help'):
            text = "Example for learning: !pyneo is a mobile framework, Example for read: ?pyneo, Example with username: ?pyneo PBeck - !facts gives a overview."
            self.sendChannel(text, connection, event)

        elif msg.startswith('!delete '): # space important
            word = msg.lstrip('!').split() # space important
            if len(word) == 2:
                buzzword = word[1]
                self.deletefact(buzzword, connection, event)

        elif msg.startswith('!'):
            word = msg.lstrip('!').split()
            if len(word) > 1:
                buzzword = word[0]
                descriptions = ' '.join(word[1:])
                print descriptions
                self.learnfact(buzzword, descriptions, connection, event)
        
        if msg.startswith('?'):
            word = msg.lstrip('?').split()
            if len(word) != 0:
                buzzword = word[0]
                if len(word) == 2:
                    user = word[1]
                    self.outputfact(buzzword, connection, event, user)
                else:
                    self.outputfact(buzzword, connection, event)

    def gitupdate(self, git, repolist, connection, event):#, connection, event):#i, git, repolist):
        minute = time.strftime("%M%S",time.gmtime())
        if minute in ('0000','1500','3000','4500'):
            time.sleep(1)
            self.updates = git.main(repolist)
            self.sendmessage(connection, event)

    def sendmessage(self, connection, event):
            for channel in channels:
                for update in self.updates:
                    connection.privmsg(channel, update)
                    time.sleep(2) # kick protection :)
   
    def main(self, botname, channel, network, port, username, repolist, factsdb):
    
        git = gitcheck.Gitcheck()
        updates = ()

        self.con = sqlite3.connect(factsdb)
        self.con.text_factory = str
        self.cur = self.con.cursor()
        try:
            self.cur.execute('''CREATE TABLE facts(buzzword TEXT, description TEXT)''')
        except:
            print 'Database already exists'

        irc = irclib.IRC()
        try:
            c = irc.server().connect(network, port, botname, username=username)
        except irclib.ServerConnectionError, x:
            print x
            sys.exit(1)
        
        c.add_global_handler("welcome", self.connect)
        c.add_global_handler('nicknameinuse', self.nicknameinuse)
        c.add_global_handler('pubmsg', self.pubmsg)
        c.add_global_handler('ping', self.pong)
        while 1:
            self.gitupdate(git, repolist, c, c)
            irc.process_once()

            if not c.is_connected(): # reconnect if disconnect
                self.connect(c, c)
            
            time.sleep(0.02)


if __name__ == '__main__':
    
    botname = '__pyneo'
    username = 'pyneo' # only alphanumerical characters
    channels = ['#pyneo.org'] # you can add as much channels as you like => channels = ['channel1','channel2','channel3']
    network = 'chat.freenode.net'
    port = 6667

    dbname = "facts.db" # database for saving the facts 
    factsdb = gitcheck.Gitcheck().absolutePath() + dbname # get the absolutepath for the database 
    
    repolist = [ # a list with all controlled repositorys
    ['http://git.gitorious.org/epydial/epydial.git','master'],
    ['http://git.gitorious.org/epydial/epydial.git','pyneo-1.32'],
    ['http://git.gitorious.org/epydial/epydial-new.git','master'],
    ['http://git.pyneo.org/browse/cgit/paroli','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-pyneod','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-pybankd','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-pyrssd','master'],
#    ['http://git.pyneo.org/browse/cgit/pyneo-pyaudiod','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-zad','master'],
    ['http://git.pyneo.org/browse/cgit/python-pyneo','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-resolvconf','master'],
    ['http://git.pyneo.org/browse/cgit/gsm0710muxd','master'],
    ['http://git.pyneo.org/browse/cgit/gllin','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-pygsmd','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo','master'],
    ['http://git.pyneo.org/browse/cgit/python-ijon','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-zadthemes','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-gentoo','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-debian','master'],
    ['http://git.pyneo.org/browse/cgit/enlua','master'],
    ['http://git.pyneo.org/browse/cgit/python-aqbanking','master'],
    ['http://git.pyneo.org/browse/cgit/python-directfb','master'],
    ['http://git.pyneo.org/browse/cgit/bwbasic','master'],
    ['http://git.pyneo.org/browse/cgit/robots','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-zadosk','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-zadwm','master'],
    ]

    bot = Gitbot()
    bot.main(botname, channels, network, port, username, repolist, factsdb)
