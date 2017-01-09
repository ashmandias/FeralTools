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
import tinyurl
import dns
import re

feral_channel = "##feral"
max_url_length = 15
feralbot_nick = "FeralBot"

def shortenURL(url):
    if len(url) > max_url_length:
        return tinyurl.create_one(url)
    else:
        return url

def shouldReply(irc,msg):
    addressedBy = msg.args[0]
    botCommand = msg.args[1]
    nicks = irc.state.channels[feral_channel].users
    
    if not addressedBy.startswith('#'):
        return True
    elif botCommand.startswith('*'):
        return True
    elif botCommand.startswith('!') and feralbot_nick not in nicks:
        return True
    else:
        return False


# FAQ URLs
URL_faq         = "https://github.com/feralhosting/faqs-cached"
URL_faq_autodl  = "https://github.com/feralhosting/faqs-cached/blob/master/08%20Software/04%20Autodl-irssi%20-%20Installation%20and%20Configuration.md"
URL_faq_plex    = "https://github.com/feralhosting/faqs-cached/blob/master/08%20Software/27%20Plex.md"
URL_faq_reroute = "https://github.com/feralhosting/faqs-cached/blob/master/06%20Other%20software/04%20Automated%20Reroute.md"
URL_faq_restart = "https://github.com/feralhosting/faqs-cached/blob/master/02%20Installable%20software/04%20Restarting%20-%20rtorrent%20-%20Deluge%20-%20Transmission%20-%20MySQL.md"
URL_faq_ssh     = "https://github.com/feralhosting/faqs-cached/blob/master/03%20SSH/01%20SSH%20Guide%20-%20The%20Basics.md"

# Other URLS
URL_irc_help    = "http://rurounijones.github.io/blog/2009/03/17/how-to-ask-for-help-on-irc/"
URL_OpenVPN     = "https://github.com/feralhosting/faqs-cached/blob/master/02%20Installable%20software/10%20OpenVPN%20-%20How%20to%20connect%20to%20your%20vpn.md"
URL_passwords   = "https://github.com/ashmandias/FeralInfo#password-questions"
URL_payments    = "https://github.com/ashmandias/FeralInfo#payments"
URL_pricing     = "http://web.archive.org/web/20160220120121/https://www.feralhosting.com/pricing"
URL_quota       = "https://github.com/feralhosting/feralfilehosting/tree/master/Feral%20Wiki/SSH/Check%20your%20disk%20quota%20in%20SSH"
URL_urls        = "https://github.com/ashmandias/FeralInfo#application-access"
URL_reroute     = "https://network.feral.io/reroute"
URL_vampire     = "http://www.skidmore.edu/~pdwyer/e/eoc/help_vampire.htm"
URL_kitten      = "http://www.emergencykitten.com/"
URL_kittens     = "http://thecatapi.com/"

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
    def reply(self, irc, args, reply):
        """
        formats replies
        """
        if len(args) >=1:
            reply = str(args[0]) + ": " + reply
        matches=re.findall("(?P<url>https?://[^\s]+)", reply)
        for match in matches:
            reply = reply.replace(match,shortenURL(match))
        irc.reply(reply, prefixNick=False)

    def validHost(self, host):
        host = str.replace(host,".feralhosting.com","")
        myResolver = dns.resolver.Resolver()
        try:
            myAnswers = myResolver.query(host + ".feralhosting.com", "A")
            for rData in myAnswers:
                return (True,str(rData),host)
        except:
            return (False,None,None)

    def help(self, irc, msg, args):
        """
        Usage: urls [user] Pm (optionally to a different user) with help info
        """
        nicks = irc.state.channels[feral_channel].users
        #channel_state = irc.state.channels[feral_channel]
        #nicks = list(channel_state.users)
        reply = [ "Helpful commands: ask [$user] (just ask), autodl [$user] (use any watchdir), cloudmonitor $host (widespread ping), eta [$user] (eta policy), faq [$user] (faq location), "
                , "                  help $user (send this help), helpus $user (tell them how to get help), payments [$user] (payment status and info),"
                , "                  quota [$user] (how to check quota), reroute (how to reroute), status $host [details] (checks status), "
                , "                  urls [$user] (lists client urls), vpn [$user] (how to set up OpenVPN)"
                , "Tracker commands: (check the status of services at various trackers) btn, pth, ptp"
                , "Joke    commands: cthulhu, kitten, kittens, vampire, westworld" ]
        try:
            nick = args[0]
            if (ircutils.isNick(nick) and  nick in nicks) or nick == '##feral-chat':
                self.reply(irc, args, reply="I am sending you help information in a private message. Please review it. You can test the command via PM if you like.")
                for message in reply:
                    irc.queueMsg(ircmsgs.notice(nick,message))
            else: 
                self.reply(irc, args, "You need to specify a nick in " + feral_channel + " to send to")
        except:
            self.reply(irc, args, "You need to specify a nick in " + feral_channel + " to send to")

    def helpus(self, irc, msg, args):
        """
        Usage: urls [user] Pm (optionally to a different user) with help info
        """
        nicks = irc.state.channels[feral_channel].users
        #channel_state = irc.state.channels[feral_channel]
        #nicks = list(channel_state.users)
        reply = ["Help us help you. Please include a description of any problem you are having, along with any relevant information -- "
                , "such as what you are doing, trying to do, or what guide you are following, and any errors you are getting."
                , "Additionally, most issues are isolated to one server (or even one account), so please tell us what service and server you are on" 
                , "Tips for getting help on IRC can be found at: " + URL_irc_help ]
                
        try:
            if ircutils.isNick(args[0]) and args[0] in nicks:
                self.reply(irc, args, "I am sending you information on how to get the most valuable help, and how to help us help you.")
                for message in reply:
                    irc.queueMsg(ircmsgs.notice(args[0],message))
            else: 
                self.reply(irc, args, "You need to specify a nick in " + feral_channel + " to send to")
        except:
            self.reply(irc, args, "You need to specify a nick in " + feral_channel + " to send to")

# serious

    def accessdenied(self, irc, msg, args):
        """
        What "access denied" means
        """
        reply = "If you are getting \"" + ircutils.mircColor("Access Denied","red") + "\" when attempting to SSH into your server, either you are not using the SSH password (different than most of the others), you have the wrong username, or you have the wrong hostname."
        self.reply(irc, args, reply)

    def ask(self, irc, msg, args):
        """
        "Please don't ask to ask, just ask your question"
        """
        reply = "Please don't ask to ask, just ask your question"
        self.reply(irc, args, reply)

    def autodl(self, irc, msg, args):
        """
        """
        reply = "Tip: autodl-irssi can be used with any torrent client -- just use the watchdir action, and point the torrent at the appropriate watchdir. More here: " + URL_faq_autodl
        self.reply(irc, args, reply)

    def autodlerror(self, irc, msg, args):
        """
        helper for \"Make sure autodl-irssi is started and configured properly\" regex
        """
        reply = "If you are getting the error \"" + ircutils.mircColor("Make sure autodl-irssi is started and configured properly","red") + "\", make sure one, and only one instance of irssi is running. If this does not resolve the issue, please run the script at: " + URL_faq_autodl
        self.reply(irc, args, reply)

    def cloudmonitor(self, irc, msg, args, host):
        """
        $host
        """
        response=self.validHost(host)
        if response[0]:
            reply = "To view a worldwide ping to " + ircutils.mircColor(host.capitalize(), "green") + ", please visit the following link:http://cloudmonitor.ca.com/en/ping.php?vtt=1387589430&varghost=" + host + ".feralhosting.com&vhost=_&vaction=ping&ping=start"
        else:
            reply = "The host: " + ircutils.mircColor(host.capitalize(), "red") + " does not appear to be a valid Feral host."
        self.reply(irc, args, reply)
            
    cloudmonitor = wrap(cloudmonitor,['anything'])

    def eta(self, irc, msg, args):
        """
        Usage: eta [user] reply (optionally to a different user) with the feral ETA policy
        """
        reply = "Feralhosting typically does not give ETAs on ongoing work. They prefer to focus on getting a solution in place over making estimates. They try to reply to tickets and emails in under 1 business day."
        self.reply(irc, args, reply)

    def faq(self, irc, msg, args):
        """
        Usage: faq [user] reply (optionally to a different user) with the FAQ location
        """
        reply = "You can find the Feral FAQ at " + URL_faq
        self.reply(irc, args, reply)

    def ip(self,irc,msg,args):
        """
        Usage: ip HOST
        """
        if len(args) >=1:
            response = self.validHost(args[0])
        else:
            irc.reply("Please use the command \"ip HOST\"")
            return
        host = response[2]
        if response[0]:
            ip = response[1]
            irc.reply("The IP for " + ircutils.mircColor(host.capitalize(),"green") + " is: " + ircutils.mircColor(ip,"green"))
            return
        else:
            irc.reply("It appears that " + ircutils.mircColor(args[0],"red")+ " is not a valid name of a feral host")
            return

# Pair
    def _status(self,irc,args,host,details):
        """
        Usage: feralstatus HOST - this will send 3 pings, and then check for FTP and SSH connectivity.
        """
        host = str.replace(host,".feralhosting.com","")
        if not host.isalpha():
            self.reply(irc, args, "Please use only the short hostname of a feral host")
            return
        irc.reply(check_output([os.environ['HOME'] + "/checks/check_server.sh", host, details]), prefixNick=False)

    #def status(self, irc, msg, args, host):
    def status(self, irc, msg, args):
        """
        Usage: status HOST [details] - this will send 3 pings, and then check for FTP and SSH connectivity.
        """
        if len(args) >=1:
            host=args[0]
        else:
            irc.reply("Please use the command \"status HOST\"")
            return
        if len(args) >=2:
            details='true'
        else:
            details='false'
        check_thread = threading.Thread(target=self._status, args=(irc,args,host,details))
        check_thread.start()
        irc.reply("Feral status: https://status.feral.io/ | Overview status: https://thehawken.org/fs | specific host status to follow shortly...", prefixNick=False)
#/Pair


    def passwords(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "Please see the following link for password recovery tips: " + URL_passwords
        self.reply(irc, args, reply)

    def payments(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "Please see  " + URL_payments + " (or the topic) for payment details"
        self.reply(irc, args, reply)

    def plex(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "Plex is now available. Please see: " + URL_faq_plex + " for details"
        self.reply(irc, args, reply)

    def pricing(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "The old pricing page can be found at " + URL_pricing
        self.reply(irc, args, reply)

    def quota(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "You can either run 'du --si -s ~' in ssh, or follow " + URL_quota + " to tell how much disk space you are using. 'df -h / ~' will check the free space on the OS drive (/) and your drive (~) as well"
        self.reply(irc, args, reply)

    def vpn(self, irc, msg, args):
        """
        Usage: vpn [user] reply (optionally to a different user) with OpenVPN install instructions
        """
        reply = "You can find the documentation for installing and configuring OpenVPN at " + URL_OpenVPN
        self.reply(irc, args, reply)

    def reroute(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "Typically speed issues between you and feral (downloading files to your home) are a result of issues on your ISP. You can attempt to reroute traffic around the problem with " + URL_reroute + " or " + URL_faq_reroute + " (if you have Bash installed locally)"
        self.reply(irc, args, reply)

    def restart(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "Please see the FAQ here on how to restart software: " + URL_faq_restart
        self.reply(irc, args, reply)

    def rtorrenterror(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "The errors\"" + ircutils.mircColor("torrent list not yet available connection to rtorrent not established", "red") + "\" or \"" + ircutils.mircColor("No connection to rTorrent. Check if it is really running.", "red") + "\" typically means rtorrent is either busy, or not running. Try to restart it with: " + URL_faq_restart
        self.reply(irc, args, reply)

    def ssh(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "The SSH FAQ can be found at " + URL_faq_ssh
        self.reply(irc, args, reply)

    def urls(self, irc, msg, args):
        """
        Usage: urls [user] reply (optionally to a different user) with URL locations
        """
        reply = "You can find the URLs to access your applications at " + URL_urls
        self.reply(irc, args, reply)

    def vampire(self, irc, msg, args):
        """
        Usage:
        """
        reply = "You might find this link helpful in avoiding feeding (or being) a help vampire: " + URL_vampire
        self.reply(irc, args, reply)

# jokes

    def cthulhu(self, irc, msg, args):
        """
        Usage:
        """
        reply = "Ia! Ia! Cthulhu fhtagn! Ph'nglui Mglw'nafh Cthulhu R'lyeh wgah'nagl fhtagn!"
        self.reply(irc, args, reply)

    def kitten(self, irc, msg, args):
        """
        Usage:
        """
        reply = "Here, have a kitten! " + URL_kitten
        self.reply(irc, args, reply)

    def kittens(self, irc, msg, args):
        """
        Usage:
        """
        reply = "KITTENS FOR EVERYONE! " + URL_kittens
        self.reply(irc, args, reply)

    def westworld(self, irc, msg, args):
        """
        Usage:
        """
        reply = "Nothing can possibly go wrong... go wrong... go wrong... go wrong..."
        self.reply(irc, args, reply)

    def test(self, irc, msg, args):
        """
        Usage: 
        """
#        if shouldReply(irc,msg):
#            irc.reply("I should reply")
        reply = "You might find this link helpful in avoiding feeding (or being) a help vampire: http://google.com http://fark.com https://reallylongurlforshitssake.com"
        matches=re.findall("(?P<url>https?://[^\s]+)", reply)
        for match in matches:
            reply = reply.replace(match,shortenURL(match))
        #url=re.search("(?P<url>https?://[^\s]+)", reply).group("url")
        irc.reply(reply)
        
        

Class = FeralTools


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
