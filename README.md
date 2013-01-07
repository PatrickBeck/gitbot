# gitbot

Gitbot prints git updates to the irc network. For this it uses gitcheck.py to generate a list with all updates since the last posting and gitbot.py do the posting to the network.

## Features

- monitors repos and branches
- can post in more than one channel
- can save factoids

    Example for learning: !pyneo is a mobile framework, 
    Example for read: ?pyneo, 
    Example with username: ?pyneo PBeck - 
    !facts gives a overview.

## Example Configuration at the end of gitbot.py (you can use gitcheck.py for output to the terminal)

    botname = 'pyneo-bot'
    channels = ['#pyneo.org'] # you can add as much channels as you like => channels = ['channel1','channel2','channel3']
    network = 'chat.freenode.net'
    port = 6667
          
    repolist = [ # a list with all controlled repositorys
    ['http://git.gitorious.org/epydial/epydial.git','master'],
    ['http://git.gitorious.org/epydial/epydial.git','pyneo-1.32'],
    ['http://git.gitorious.org/epydial/epydial-new.git','master'],
    ['http://git.pyneo.org/browse/cgit/paroli','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-zadosk','master'],
    ['http://git.pyneo.org/browse/cgit/pyneo-zadwm','master'],
    ]

## Example entry

    16:15:04 < pyneo-bot> [epydial-new / master] F. Gau at Sat Jan 1 16:01:41 2011 on 3063127f2a... [add lock icon on main screen]

## Use it on the server

The small script runtest.py checks if gitbot.py is running. A example entry for cronjob is:

    */5 * * * * /home/user/gitbot/runtest.sh 
