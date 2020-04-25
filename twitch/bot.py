import time
from abc import ABC
import threading
import datetime

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor, ssl
from config import Config


class IRCBot(irc.IRCClient, ABC):
    MSG_PREFIX = "![Bot]! "

    def __init__(self):
        super().__init__()
        config = Config()
        self.username = config.twitch_account_name
        self.nickname = config.twitch_account_name
        self.password = config.twitch_oauth_password
        self.channel = "#" + config.twitch_channel
        self.ignore_users = config.ignore_users
        self.config = config
        self.queue = None

    def parsemsg(self, s):
        """Breaks a message from an IRC server into its prefix, command, and arguments."""
        tags = {}
        prefix = ""
        trailing = []
        s = s.decode("utf-8")
        # debug
        print(s)
        if s[0] == "@":
            tags_str, s = s[1:].split(" ", 1)
            tag_list = tags_str.split(";")
            tags = dict(t.split("=") for t in tag_list)
        if s[0] == ":":
            prefix, s = s[1:].split(" ", 1)
        if s.find(" :") != -1:
            s, trailing = s.split(" :", 1)
            args = s.split()
            args.append(trailing)
        else:
            args = s.split()
        command = args.pop(0).lower()
        return tags, prefix, command, args

    def lineReceived(self, line):
        """Parse IRC line"""

        # First, we check for any custom twitch commands
        tags, prefix, cmd, args = self.parsemsg(line)
        # IRC numeric commands
        # https://www.alien.net.au/irc/irc2numerics.html
        if cmd == "001":
            self.syslog(args[1])
        elif cmd == "002":
            self.syslog(args[1])
        elif cmd == "003":
            self.syslog(args[1])
        elif cmd == "366":
            self.syslog(args[2])
        elif cmd == "372":
            self.syslog(args[1])
        elif cmd == "376":
            # RPL_ENDOFMOTD
            self.join(self.channel)
        elif cmd == "join":
            self.syslog("JOIN {}".format(args[0]))
        elif cmd == "ping":
            self.pong(prefix)
        elif cmd == "privmsg":
            self.on_privmsg(prefix, args)

    def on_privmsg(self, prefix, args):
        username = prefix.split("!", 1)[0]
        msg = args[1]
        self.log("{}: {}".format(username, msg))
        # echo back
        self.write(msg)

    def write(self, msg):
        """Send message to channel and log it"""
        self.msg(self.channel, "{}{}".format(self.MSG_PREFIX, msg))
        self.log("{}: {}{}".format(self.username, self.MSG_PREFIX, msg))

    def pong(self, daemon):
        self.sendLine("PONG {}".format(daemon))

    def syslog(self, msg):
        self.log("*{}".format(msg))

    def log(self, msg):
        now = datetime.datetime.now()
        self.queue.put("{} {}".format(now.strftime("%H:%M:%S"), msg))

    def shutdown(self):
        self.leave(self.channel)
        self.quit()


class IRCBotFactory(protocol.ClientFactory):
    def __init__(self, queue):
        super().__init__()
        self.protocol = IRCBot
        self.wait_time = 1
        self.queue = queue
        self.bot = None
        self.shutting_down = False

    def buildProtocol(self, addr):
        bot = super().buildProtocol(addr)
        bot.queue = self.queue
        self.bot = bot
        return bot

    def clientConnectionLost(self, connector, reason):
        if self.shutting_down:
            return
        self.queue.put("Lost connection, reconnecting")
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        if self.shutting_down:
            return
        msg = "Could not connect, retrying in {}s"
        self.queue.put(msg.format(self.wait_time))
        time.sleep(self.wait_time)
        self.wait_time = min(512, self.wait_time * 2)
        connector.connect()

    def shutdown(self):
        self.shutting_down = True
        if self.bot is not None:
            self.bot.shutdown()


class IRCBotManager:
    HOSTNAME = "irc.chat.twitch.tv"
    PORT = 6697
    STOP_DELAY = 1

    def __init__(self):
        self.factory = None

    def start(self, queue):
        self.factory = IRCBotFactory(queue)
        reactor.connectSSL(self.HOSTNAME, self.PORT, self.factory, ssl.ClientContextFactory())
        threading.Thread(target=reactor.run, args=(False,)).start()

    def stop(self):
        self.factory.shutdown()
        reactor.callLater(self.STOP_DELAY, self.stop_reactor)

    def stop_reactor(self):
        reactor.callFromThread(reactor.stop)
