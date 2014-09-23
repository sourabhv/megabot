#!/usr/bin/python
import os

virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
try:
    execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    pass

#
# IMPORTANT: Put any additional includes below this line.  If placed above this
# line, it's possible required libraries won't be in your searchable path
#

from twisted.internet import reactor, protocol
from twisted.words.protocols import irc
from twisted.internet.protocol import ClientFactory


SERVER = "irc.freenode.net"
NICKNAME = '[megabot]'
PASSWORD = os.environ.get('MEGABOT_PASSWORD')
CHANNEL = '##contagious'


class Bot(irc.IRCClient):

    nickname = NICKNAME
    password = PASSWORD

    def dataReceived(self, data):
        irc.IRCClient.dataReceived(self, data)

    def signedOn(self):
        self.join(self.factory.channel)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        reactor.stop()

    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]

        # check if the bot got a private message
        if channel == self.nickname:
            _msg = "Hi %s, bots are not very good at personal chatting.\
             So why don't you use the general chat?" % user
            self.msg(user, _msg)
            return

        # Otherwise check to see if it is a message directed at bot
        if msg.startswith('!megabot'):

            self.msg(channel, msg)
        elif msg.find(self.nickname) > -1 or msg.find('megabot') > -1:
            msg = 'Hi %s, please use "!megabot <your message>" to address me' % user
            self.msg(channel, msg)


class BotFactory(ClientFactory):
    protocol = Bot

    def __init__(self):
        self.channel = CHANNEL

if __name__ == "__main__":
    reactor.connectTCP(SERVER, 8051, BotFactory())
    reactor.run()
