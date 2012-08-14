###
# Copyright (c) 2012, MrLoom
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import time
import socket
import struct
import pickle
import argparse
import hashlib

class LichtClient(object):
    
    def __init__(self, address, port):
        self.sock = socket.socket( socket.AF_INET, # lol, internet
                              socket.SOCK_DGRAM ) # UDP
        self.address = address
        self.port = port
    
    def sendCommand(self, command, params):
        pickled = pickle.dumps([command,params])
        checksum = hashlib.sha256(pickled + "TESTSALT").hexdigest()[:16]
        stream = checksum + pickled
        self.sock.sendto(stream, (self.address, self.port))


class LED(callbacks.Plugin):
    """Add the help for "@plugin help LED" here
    This should describe *how* to use this plugin."""

    def __init__(self, irc):
        self.__parent = super(LED, self)
        self.__parent.__init__(irc)

        self.lichtClient = LichtClient('192.168.178.56', 16321)

    def fade(self, irc, msg, args, red, green, blue, flag):
        red = int(red)
        green = int(green)
        blue = int(blue)
        if 0 <= red  <= 255 and 0 <= green <= 255 and 0 <= blue <= 255:
            self.lichtClient.sendCommand(3, ((red, green, blue)))
            reply = u"Ok."
        else:
            reply =  u"I'm sorry, Dave. I'm afraid I can't do that."
        if flag != 'quiet':
            irc.reply(reply)
    fade = wrap(fade, ['somethingWithoutSpaces', 'somethingWithoutSpaces', 'somethingWithoutSpaces', optional('somethingWithoutSpaces')])

    def flash(self, irc, msg, args, flag):
        self.lichtClient.sendCommand(2, ((0,0,0)))
        if flag != 'quiet':
            irc.reply("Ok.")
    flash = wrap(flash, [optional('somethingWithoutSpaces')])

    def temp(self, irc, msg, args):
        fw = file("/var/tmp/temp", "r")
        temp = fw.read()
        temp = temp[:-1]
        fw.close()
        irc.reply("Die Temperatur in MrLooms Zimmer betraegt %s Grad Celsius" % temp)

    pass


Class = LED


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
