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
from dns import *
import re
import urllib

feral_channel = "##feral"
max_url_length = 15
feralbotNick = "FeralBot"
hadalyNick = "Hadaly"
benbotNick = "BenBot"
Base_github = "feralhosting"
Repo_name = "wiki"

def shortenURL(url):
    if len(url) > max_url_length:
        try:
            return tinyurl.create_one(url)
        except:
            return url
    else:
        return url

def shouldReply(irc,msg):
    addressedBy = msg.args[0]
    botCommand = msg.args[1]

    if addressedBy.startswith('#'):
        nicks = irc.state.channels[addressedBy].users
    else:
        return True
    
    if botCommand.startswith('*'):
        return True
    elif botCommand.startswith('!') and feralbotNick not in nicks:
        return True
    elif botCommand.startswith('$') and benbotNick not in nicks:
        return True
    elif botCommand.startswith('!') and hadalyNick not in nicks:
        return True
    else:
        return False


def wrapHelp(prefix,toWrap):
    lineLength = 300
    reply = [prefix]
    line = 0
    for element in sorted(toWrap):
        if len(element) == 2:
            command = element[0]
            description = ": " + element[1]
        else:
            command = element
            description = ""
        if len(reply[line]) + len(str(command) + str(description)) < lineLength:
            reply[line] += " " + ircutils.mircColor(command, "green") + description + ","
        else:
            line += 1
            reply.append(ircutils.mircColor(command, "green") + ",")
    return reply

# FAQ URLs
URL_faq         = "https://github.com/" + Base_github + "/" + Repo_name 
URL_faq_autodl  = "https://github.com/" + Base_github + "/" + Repo_name + "/blob/master/08%20Software/04%20Autodl-irssi%20-%20Installation%20and%20Configuration.md"
URL_faq_plex    = "https://github.com/" + Base_github + "/" + Repo_name + "/blob/master/08%20Software/27%20Plex.md"
URL_faq_plugins = "https://github.com/" + Base_github + "/" + Repo_name + "/blob/master/02%20Installable%20software/16%20ruTorrent%20-%20Plugins.md"
URL_faq_rclone  = "https://github.com/" + Base_github + "/" + Repo_name + "/blob/master/08%20Software/21%20rclone%20-%20Cloud%20Service%20Syncing.md"
URL_faq_reroute = "https://github.com/" + Base_github + "/" + Repo_name + "/blob/master/06%20Other%20software/04%20Automated%20Reroute.md"
URL_faq_restart = "https://github.com/" + Base_github + "/" + Repo_name + "/blob/master/02%20Installable%20software/04%20Restarting%20-%20rtorrent%20-%20Deluge%20-%20Transmission%20-%20MySQL.md"
URL_faq_search  = "https://github.com/" + Base_github + "/" + Repo_name + "/search?q="
URL_faq_ssh     = "https://github.com/" + Base_github + "/" + Repo_name + "/blob/master/03%20SSH/01%20SSH%20Guide%20-%20The%20Basics.md"
URL_faq_www     = "https://github.com/" + Base_github + "/" + Repo_name + "/blob/master/05%20HTTP/01%20Putting%20your%20WWW%20folder%20to%20use.md"
URL_faq_nginx   = "https://github.com/" + Base_github + "/" + Repo_name + "/blob/master/05%20HTTP/10%20Updating%20Apache%20to%20nginx.md"

URL_OpenVPN     = "https://github.com/" + Base_github + "/" + Repo_name + "/blob/master/02%20Installable%20software/10%20OpenVPN%20-%20How%20to%20connect%20to%20your%20vpn.md"
URL_quota       = "https://github.com/" + Base_github + "/feralfilehosting/tree/master/Feral%20Wiki/SSH/Check%20your%20disk%20quota%20in%20SSH"

# Other URLS
URL_feralaliases = "https://git.io/vsuVp"
URL_irc_help    = "http://rurounijones.github.io/blog/2009/03/17/how-to-ask-for-help-on-irc/"
URL_passwords   = "https://github.com/ashmandias/FeralInfo#password-questions"
URL_passwords2  = "https://www.feralhosting.com/login/recover/guide"
URL_payments    = "https://github.com/ashmandias/FeralInfo#payments"
URL_pricing     = "http://web.archive.org/web/20160220120121/https://www.feralhosting.com/pricing"
URL_urls        = "https://github.com/ashmandias/FeralInfo#application-access"
URL_reroute     = "https://network.feral.io/reroute"
URL_vampire     = "http://www.skidmore.edu/~pdwyer/e/eoc/help_vampire.htm"
URL_kitten      = "http://www.emergencykitten.com/"
URL_kittens     = "http://thecatapi.com/"

volunteers      = "liriel, ozymandias, bobbyblack, and many others"


helpCommands =  [["ask [$user]","just ask"],["autodl [$user]","use any watchdir"],["cloudmonitor $host","widespread ping"],["eta [$user]","eta policy"],["faq [$user]","faq location"]]
helpCommands += [["feralaliases [$user]"," how to install"],["feraliostat [$user]","how to use"],["help $user","send this help"],["helpus $user","tell them how to get help"]]
helpCommands += [["payments [$user]","payment status and info"],["quota [$user]","how to check quota"],["reroute [$user]","how to reroute"],["status $host [details]","checks status"]]
helpCommands += [["urls [$user]","lists client urls"],["vpn [$user]","how to set up OpenVPN"],["volunteers [$user]","talk about volunteers"],["plexupdate [$user]","host to update plex"],["geoip [$user]","describe geoip system"],["invites [$user]", feral_channel + " invite policy"]]
helpCommands += [["t [$user]","displays the topic of " + feral_channel],["staff|notstaff [$user]","how to get staff"],["ipt [$user]","IPT infographic"]]
helpCommands += [["www [$user]","link to faq on using the www dir"],["nginx","Install nginx"],["upgrade","How to change plans"]]
helpCommands += [["cache [user]","tell user to clear cache"]]
helpCommands += [["salt [user]","explain salt+hash"]]

trackerCommands = ["btn","pth","ptp","ggn","ipt"]
jokeCommands = ["cthulhu","kitten","kittens","vampire|garlic","westworld","oneofus","comcast","mindreader","wave"]

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

        try:
            nick = args[0]
        except:
            nick = msg.nick

        if (ircutils.isNick(nick) and  nick in nicks) or nick == '##feral-chat' or nick == '#testytest':
            self.reply(irc, args, reply="I am sending you help information in a message only you can see. Please review it (you may need to look in other IRC windows, depending on client). You can test the commands via PM if you like.")
            reply  = wrapHelp(ircutils.mircColor("Helpful commands: ", "red"), helpCommands)
            reply += wrapHelp(ircutils.mircColor("Tracker commands (check status of trackers): ", "red"), trackerCommands)
            reply += wrapHelp(ircutils.mircColor("Joke commands: "   , "red"), jokeCommands)
            for message in reply:
                irc.queueMsg(ircmsgs.notice(nick,message))
        else: 
            self.reply(irc, args, "You need to specify a nick in " + feral_channel + " to send to")

    def helpus(self, irc, msg, args):
        """
        Usage: urls [user] Pm (optionally to a different user) with help info
        """
        nicks = irc.state.channels[feral_channel].users
        
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

    def cache(self, irc, msg, args):
        """
        """
        reply = "If you are getting the message \"" + ircutils.mircColor("If you are a user and are looking for your data or installed applications please visit the software page in the manager.","red") + "\" when trying to access recently installed software, please clear your browser cache and try again."
        self.reply(irc, args, reply)

    def cloudmonitor(self, irc, msg, args, host):
        """
        $host
        """
        response=self.validHost(host)
        if response[0]:
            reply = "To view a worldwide ping to " + ircutils.mircColor(host.capitalize(), "green") + ", please visit the following link: http://cloudmonitor.ca.com/en/ping.php?vtt=1387589430&varghost=" + host + ".feralhosting.com&vhost=_&vaction=ping&ping=start"
        else:
            reply = "The host: " + ircutils.mircColor(host.capitalize(), "red") + " does not appear to be a valid Feral host."
        self.reply(irc, args, reply)
            
    cloudmonitor = wrap(cloudmonitor,['anything'])

    def dafuq(self, irc, msg, args):
        """
        Usage: 
        """
        reply = ircutils.mircColor("NOPE!","red")
        self.reply(irc, args, reply)

    def declined(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "If your payment was declined, please check that all the information you entered was accurate and correct, that you are not using a VPN or a proxy. Those are the typical reasons Stripe may decline a payment. Otherwise, ask your bank for details."
        self.reply(irc, args, reply)

    def disabled(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "Disabled slots will be automatically enabled soon.  No one in IRC can enable it for you. No ticket is needed at this time. Once it is reenabled, please give it 10-15 minutes to restart all services."
        self.reply(irc, args, reply)
    
    def diskio(self, irc, msg, args):
        self.feraliostat(irc, msg, args);

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

    def faqsearch(self, irc, msg, args):
        """
        Usage: search
        """
        if len(args) >=1:
            reply = "Feral FAQ search result: " + URL_faq_search + urllib.quote_plus(args[0])
        else:
            reply = "Please provide a term to search for."
        irc.reply(reply, prefixNick=False)

    def feralaliases (self, irc, msg, args):
        """
        How to install FeralAliases
        """
        reply = "To install some commands to help us help you, please run the following in SSH (NOTE: it is -q as in quiet O as in Output) : wget -qO ~/.feral_aliases " + URL_feralaliases + " && . ~/.feral_aliases"
        self.reply(irc, args, reply)

    def feraliostat (self, irc, msg, args):
        """
        How to install FeralAliases
        """
        reply = "To run the feral_iostat command please install the feral_aliases script (say \"*feral_aliases\" to learn how) and run feral_iostat"
        self.reply(irc, args, reply)

    def garlic (self, irc, msg, args):
        """
        How to install FeralAliases
        """
        self.vampire(irc, msg, args)        

    def geoip (self, irc, msg, args):
        """
        How to install FeralAliases
        """
        reply = "GeoIP data is the GeoIP companies best guess as to where an IP is physically located. They often use the official address of a company and not the location of the servers. See also: goo.gl/2P2EG4"
        self.reply(irc, args, reply)

    def issues (self, irc, msg, args):
        """
        """
        reply = "Current issues: unclaimed slots are disabled (say *unclaimed for details). Disabled slots are automaticall enabled (say *disabled for details)"
        self.reply(irc, args, reply)

    def ipt (self, irc, msg, args):
        """
        ipt info
        """
        reply = "For information about IPT, please check here: http://i.imgur.com/b4cCrsJ.png"
        self.reply(irc, args, reply)

    def nginx (self, irc, msg, args):
        """
        ipt info
        """
        reply = "To find out how to install nginx: " + URL_faq_nginx
        self.reply(irc, args, reply)

    def notstaff (self, irc, msg, args):
        self.staff(irc, msg, args)

    def openvpn(self, irc, msg, args):
        self.vpn(irc,msg,args);

    def invites (self, irc, msg, args):
        """
        """
        reply = "Feralhosting's owner has requested that we do not ask for, or offer invites to any tracker here. You can discuss how to get them, or if they are worth getting, however"
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
    def searchfaq(self, irc, msg, args):
        self.faqsearch(irc, msg, args);

    def status(self, irc, msg, args):
        """
        Usage: status HOST [details] - this will send 3 pings, and then check for FTP and SSH connectivity.
        """
        if len(args) >=1:
            host=args[0]
        else:
            irc.reply("Please use the command \"*status HOST\"")
            return
        if not self.validHost(host)[0]:
            irc.reply( host + " does not appear to be a valid feral hostname")
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
        reply = "Please see the following link for password recovery tips: " + URL_passwords + " or " + URL_passwords2
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

    def plugins(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "To install plugins in rutorrent, please see: " + URL_faq_plugins + " ."
        self.reply(irc, args, reply)

    def plexupdate(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "To upgrade to the latest *Feral supported version* (currently 1.3.4.3285, not always the latest Plex version) of plex please run this: kill $(ps x | pgrep -fu $(whoami) 'plexmediaserver') &> /dev/null; rm -rf ~/private/plex && mkdir -p ~/private/plex"
        self.reply(irc, args, reply)
        reply = "ALTERNATIVELY you can try downloading the .deb file and running: dpkg-deb -x plexmediaserver_*_amd64.deb ~/private/plex ; kill $(ps x | pgrep -fu $(whoami) 'plexmediaserver') -- this allows you to install arbitrary, untested versions of Plex (including Plex Pass)." 
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

    def rclone(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "You can install rclone on feral with the following documentation -- but you cannot use FUSE" + URL_faq_rclone
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

    def salt(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "The phrase \"" + ircutils.mircColor("stored as a sha512 salt+hash","red") + "\" means the system doesn't know it and you should continue to use the one used to recover your slot. If you've lost that please open a support ticket and ask for a reset"
        self.reply(irc, args, reply)

    def ssh(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "The SSH FAQ can be found at " + URL_faq_ssh
        self.reply(irc, args, reply)

    def staff(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "If you actually need staff, you should send an email to the support address -- but you will likely be suprised what the customers chatting in IRC can help with."
        self.reply(irc, args, reply)

    def t(self, irc, msg, args):
        """
        Usage: 
        """
        reply = "The topic of " + feral_channel + " is: " + irc.state.channels[feral_channel].topic
        self.reply(irc, args, reply)

    def unclaimed(self, irc, msg, args):
        reply = ircutils.mircColor("All","red") + " unclaimed slots have been " + ircutils.mircColor("disabled/suspended","red") + ". They will *not* be deleted immediately. Please claim your slot at https://www.feralhosting.com/login/ now! Please see http://tinyurl.com/zvsxc5t or http://tinyurl.com/zxjdszf for password recovery tips!"
        self.reply(irc, args, reply)
        reply = "Tips: 1. If you are clicking the " + ircutils.mircColor("'reset'", "red" ) + " button, you are likely making a " + ircutils.mircColor("huge", "red") + " mistake. 2. Use the same browser for the whole process. 3. At this point in time " + ircutils.mircColor("*full payment of your balance is not required*", "red") + ". Please pay as soon as you can, but your slot will " + ircutils.mircColor("*not*", "red") +" be disabled for non-payment.... yet."
        self.reply(irc, args, reply)
        reply = "Tips (cont.) 4. If you cannot recall what the existing day-of-month your payment is due, please select a date that is convienient for you."
        self.reply(irc, args, reply)

    def reclaim(self, irc, msg, args):
        self.unclaimed(irc, msg, args);

    def upgrade(self, irc, msg, args):
        """
        Usage:
        """
        reply = "You can upgrade (or downgrade, or switch servers) your slot by purchasing a new slot, transfering the data (or having staff do it for you) and then getting a refund on the old slot. There is no way to do an in-place upgrade."
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

    def volunteers(self, irc, msg, args):
        """
        Usage:
        """
        reply = volunteers + " are all just volunteers. They are not staff, they are customers that enjoy helping other users in their spare time."
        self.reply(irc, args, reply)

    def www(self, irc, msg, args):
        """
        Usage:
        """
        reply = "Putting your WWW folder to use: " + URL_faq_www
        self.reply(irc, args, reply)

# jokes

    def cthulhu(self, irc, msg, args):
        """
        Usage:
        """
        reply = "Ia! Ia! Cthulhu fhtagn! Ph'nglui Mglw'nafh Cthulhu R'lyeh wgah'nagl fhtagn!"
        self.reply(irc, args, reply)

    def comcast(self, irc, msg, args):
        """
        Usage:
        """
        reply = "COOOOOMCAAAAAST! http://tinyurl.com/jwttsmj"
        self.reply(irc, args, reply)

    def gelliss(self, irc, msg, args):
        """
        Usage:
        """
        reply = "That's the way she goes. Sometimes she goes and sometimes she doesnt cuz that's the f'n way she goes"
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

    def mindreader(self, irc, msg, args):
        """
        Usage:
        """
        reply = "As far as we are aware, no one here is a mind reader, so it is really hard for us to answer that question. Could you please provide more details, so we may more easily help you?"
        self.reply(irc, args, reply)

    def westworld(self, irc, msg, args):
        """
        Usage:
        """
        reply = "Nothing can possibly go wrong... go wrong... go wrong... go wrong..."
        self.reply(irc, args, reply)

    def oneofus(self, irc, msg, args):
        """
        Usage:
        """
        reply = "One of us! One of us! Gooble Gobble! One of us!"
        self.reply(irc, args, reply)

    def wave(self, irc, msg, args):
        """
        Usage:
        """
        reply = "o/ "
        irc.reply(reply + msg.nick,prefixNick=False)


    def test(self, irc, msg, args):
        """
        Usage: 
        """

        irc.reply(irc.state.channels[feral_channel].topic)        
        

Class = FeralTools


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
