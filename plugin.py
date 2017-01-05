###
# Copyright (c) 2017, Ashmandias
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
import supybot.ircmsgs as ircmsgs
from subprocess import check_output
import subprocess
import threading
import os

feral_channel = "##feral"

# FAQ URLs
URL_faq = "https://github.com/feralhosting/faqs-cached"
URL_faq_reroute = "https://www.feralhosting.com/faq/view?question=292"
URL_faq_ssh = "https://github.com/feralhosting/faqs-cached/blob/master/03%20SSH/01%20SSH%20Guide%20-%20The%20Basics.md"

# Other URLS
URL_OpenVPN = "https://github.com/feralhosting/faqs-cached/blob/master/02%20Installable%20software/10%20OpenVPN%20-%20How%20to%20connect%20to%20your%20vpn.md"
URL_passwords = "https://github.com/ashmandias/FeralInfo#password-questions"
URL_payments = "https://github.com/ashmandias/FeralInfo#payments"
URL_pricing = "http://web.archive.org/web/20160220120121/https://www.feralhosting.com/pricing"
URL_quota = "https://github.com/feralhosting/feralfilehosting/tree/master/Feral%20Wiki/SSH/Check%20your%20disk%20quota%20in%20SSH"
URL_urls = "https://github.com/ashmandias/FeralInfo#application-access"
URL_reroute = "https://network.feral.io/reroute"
URL_vampire = "http://www.skidmore.edu/~pdwyer/e/eoc/help_vampire.htm"
URL_kitten = "http://www.emergencykitten.com/"
URL_kittens = "http://thecatapi.com/"

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('FeralTools')
except:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x:x

class FeralTools(callbacks.Plugin):
    """Add the help for "@plugin help FeralTools" here
    This should describe *how* to use this plugin."""
    threaded = True

# Helpers
    def reply(self, irc, msg, args):
        """
        formats replies
        """
        print (args)
	if len(args) >=2:
            reply = str(args[1]) + ": " + str(args[0])
        irc.reply(reply, prefixNick=False)

    def help(self, irc, msg, args):
        """
        Usage: urls [user] Pm (optionally to a different user) with help info
        """
        nicks = irc.state.channels[feral_channel].users
        #channel_state = irc.state.channels[feral_channel]
        #nicks = list(channel_state.users)
        reply = [ "Helpful commands: ask(just ask), autodl(use any watchdir), cloudmonitor(widespread ping), faq(faq location), "
                ,"                  payments(payment status and info), quota(how to check quota), reroute(how to reroute), "
                ,"                  status(checks status), urls(lists client urls), vpn(how to set up OpenVPN)"
                , "Joke    commands: cthulhu, kitten, kittens, vampire" ]
        if len(args) >=1 and ircutils.isNick(args[0]) and args[0] in nicks:
            irc.reply(args[0] + " : I am sending you help information in a private message. Please review it. You can test the command via PM if you like.", prefixNick=False)
            for message in reply:
                irc.queueMsg(ircmsgs.notice(args[0],message))
        else: 
            irc.reply("You need to specify a nick in " + feral_channel + " to send to", prefixNick=False)

    def helpus(self, irc, msg, args):
        """
        Usage: urls [user] Pm (optionally to a different user) with help info
        """
        nicks = irc.state.channels[feral_channel].users
        #channel_state = irc.state.channels[feral_channel]
        #nicks = list(channel_state.users)
        reply = ["Help us help you. Please include a description of any problem you are having, along with any relevant information -- such as what you are doing,"
                , "trying to do, or what guide you are following."
                , "Additionally, most issues are isolated to one server (or even one account), so please tell us what service and server you are on" ]
                
        if len(args) >=1 and ircutils.isNick(args[0]) and args[0] in nicks:
            irc.reply(args[0] + " : I am sending you information on how to get the most valuable help, and how to help us help you.", prefixNick=False)
            for message in reply:
                irc.queueMsg(ircmsgs.notice(args[0],message))
        else: 
            irc.reply("You need to specify a nick in " + feral_channel + " to send to", prefixNick=False)

# serious

    def ask(self, irc, msg, args):
        """
        "Please don't ask to ask, just ask your question"
        """
        print (args)
        reply = "Please don't ask to ask, just ask your question"
        if len(args) >=1:
            reply = str(args[0]) + ": " + reply
        irc.reply(reply, prefixNick=False)

    def autodl(self, irc, msg, args):
        """
        """
        print (args)
        reply = "autodl-irssi can be used with any torrent client -- just use the watchdir action, and point the torrent at the appropriate watchdir"
        if len(args) >=1:
            reply = str(args[0]) + ": " + reply
        irc.reply(reply, prefixNick=False)

    def cloudmonitor(self, irc, msg, args, host):
        """
        """
       # print (args)
        host = str.replace(host,".feralhosting.com","")
        reply = "To view a worldwide ping to " + host + ", please visit the following link:http://cloudmonitor.ca.com/en/ping.php?vtt=1387589430&varghost=" + host + ".feralhosting.com&vhost=_&vaction=ping&ping=start"
        if len(args) >=1:
            reply = str(args[0]) + ": " + reply
        irc.reply(reply, prefixNick=False)
        cloudmonitor = wrap(cloudmonitor,['anything'])

    def faq(self, irc, msg, args):
        """
        Usage: faq [user] reply (optionally to a different user) with the FAQ location
        """
        print (args)
        reply = "You can find the Feral FAQ at " + URL_faq
        if len(args) >=1:
            reply = str(args[0]) + ": " + reply
        irc.reply(reply, prefixNick=False)

    def ip(self,irc,msg,args):
        """
        Usage: ip HOST
        """
        if len(args) >=1:
            host=args[0]
        else:
            irc.reply("Please use the command \"ip HOST\"")
            return
        host = str.replace(host,".feralhosting.com","")
        if not host.isalpha():
            irc.reply("Please use only the short hostname of a feral host")
            return
        irc.reply(check_output([os.environ['HOME'] + "/checks/check_ip.sh", host]), prefixNick=False)

# Pair
    def feralstatus(self,irc,args,host):
        """
        Usage: feralstatus HOST - this will send 3 pings, and then check for FTP and SSH connectivity.
        """
        host = str.replace(host,".feralhosting.com","")
        if not host.isalpha():
            irc.reply("Please use only the short hostname of a feral host")
            return
        irc.reply(check_output([os.environ['HOME'] + "/checks/check_server.sh", host]), prefixNick=False)

    #def status(self, irc, msg, args, host):
    def status(self, irc, msg, args):
        """
        Usage: feralstatusthread HOST - this will send 3 pings, and then check for FTP and SSH connectivity.
        """
        if len(args) >=1:
            host=args[0]
        else:
            irc.reply("Please use the command \"status HOST\"")
            return
        if host.lower() == "leon":
#            irc.reply("Latest Staff update on Leon as of Jan 4, 2017: most likely a hardware fault (NIC), need to fly over to work on it.", prefixNick=False)
            irc.reply("Host appears to be in the process of booting, please be patient while services restart.", prefixNick=False)
            return
        check_thread = threading.Thread(target=self.feralstatus, args=(irc,args,host))
        check_thread.start()
        irc.reply("Feral status:|https://status.feral.io/| Overview status:|https://thehawken.org/fs.|, specific host status to follow shortly...", prefixNick=False)
#        status = wrap(status,['anything'])
#/Pair


    def passwords(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "Please see the following link for password recovery tips: " + URL_passwords
        if len(args) >=1:
            reply = str(args[0]) + ": " + reply
        irc.reply(reply, prefixNick=False)

    def payments(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "Please see  " + URL_payments + " (or the topic) for payment details"
        if len(args) >=1:
            reply = str(args[0]) + ": " + reply
        irc.reply(reply, prefixNick=False)

    def pricing(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "The old pricing page can be found at " + URL_pricing
        if len(args) >=1:
            reply = str(args[0]) + ": " + reply
        irc.reply(reply, prefixNick=False)

    def quota(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "You can either run 'du --si -s ~' in ssh, or follow " + URL_quota
        if len(args) >=1:
            reply = str(args[0]) + ": " + reply
        irc.reply(reply, prefixNick=False)

    def vpn(self, irc, msg, args):
        """
        Usage: vpn [user] reply (optionally to a different user) with OpenVPN install instructions
        """
        reply = "You can find the documentation for installing and configuring OpenVPN at " + URL_OpenVPN
        if len(args) >=1:
            reply = str(args[0]) + ": " + reply
        irc.reply(reply, prefixNick=False)

    def reroute(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "Typically speed issues between you and feral (downloading files to your home) are a result of issues on your ISP. You can attempt to reroute traffic around the problem with " + URL_reroute + " or " + URL_faq_reroute + " (if you have Bash installed locally)"
        if len(args) >=1:
            reply = str(args[0]) + ": " + reply
        irc.reply(reply, prefixNick=False)

    def ssh(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "The SSH FAQ can be found at " + URL_faq_ssh
        if len(args) >=1:
            reply = str(args[0]) + ": " + reply
        irc.reply(reply, prefixNick=False)

    def urls(self, irc, msg, args):
        """
        Usage: urls [user] reply (optionally to a different user) with URL locations
        """
        reply = "You can find the URLs to access your applications at " + URL_urls
        if len(args) >=1:
            reply = str(args[0]) + ": " + reply
        irc.reply(reply, prefixNick=False)

    def vampire(self, irc, msg, args):
        """
        Usage:
        """
        reply = "You might find this link helpful in avoiding feeding (or being) a help vampire: " + URL_vampire
        if len(args) >=1:
            reply = str(args[0]) + ": " + reply
        irc.reply(reply, prefixNick=False)

# jokes

    def cthulhu(self, irc, msg, args):
        """
        Usage:
        """
        reply = "Ia! Ia! Cthulhu fhtagn! Ph'nglui Mglw'nafh Cthulhu R'lyeh wgah'nagl fhtagn!"
        if len(args) >=1:
            reply = str(args[0]) + ": " + reply
        irc.reply(reply, prefixNick=False)

    def kitten(self, irc, msg, args):
        """
        Usage:
        """
        reply = "Here, have a kitten! " + URL_kitten
        if len(args) >=1:
            reply = str(args[0]) + ": " + reply
        irc.reply(reply, prefixNick=False)

    def kittens(self, irc, msg, args):
        """
        Usage:
        """
        reply = "KITTENS FOR EVERYONE! " + URL_kittens
        if len(args) >=1:
            reply = str(args[0]) + ": " + reply
        irc.reply(reply, prefixNick=False)
Class = FeralTools


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
