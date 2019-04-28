import re
import typing

import irclib


def process_twitch_flags(flags) -> typing.Dict[str, typing.Union[str, typing.List[str]]]:
    # @<key>=<value>;[...]
    flags = flags[1:].split(';')
    # [<key>=<value>, [...]]
    output = {}
    for i in flags:
        i = i.split('=', 1)
        val = i[1]
        if ',' in val:
            val = val.split(',')
        output[i[0]] = val
    return output


class Message:
    @staticmethod
    def from_match(m: typing.Match[str]):
        return Message(m.string)

    @staticmethod
    def from_text(text):
        return Message(text)

    def __init__(self, args: str):
        self._type = 'raw'
        self.args: str = args
        self.outgoing = False

    def __eq__(self, other):
        if isinstance(other, Message):
            return other._type == self._type and other.args == self.args
        else:
            return False

    def __repr__(self):
        return f'RawMessage(args={self.args!r})'

    def __str__(self):
        return f'<Raw IRC message: {self.args!r}>'

    def __bytes__(self):
        if self.outgoing:
            return self.args
        else:
            return b''


class ChannelMessage(Message):
    @staticmethod
    def from_match(m: typing.Match[str]):
        new = ChannelMessage(text=m[4], user=m[2], channel=m[3])
        new.flags = process_twitch_flags(m[1])
        # new.user = m[2]
        # new.channel = m[3]
        # new.text = m[4]
        return new

    @staticmethod
    def from_text(text):

        m = re.match(irclib.PRIVMSG_PATTERN_TWITCH, text)
        if m:
            return ChannelMessage.from_match(m)
        else:
            # print(text)
            # text -> ':{user}!{user2?}@{user3?}.{host} PRIVMSG #{chan} :{msg}\r\n'
            text = text.replace('\r\n', '')
            # text -> ':{user}!{user2?}@{user3?}.{host} PRIVMSG #{chan} :{msg}'

            t = text.split(' ', 3)
            # t -> [':{user}!{user2?}@{user3?}.{host}', 'PRIVMSG', '#{chan}', ':{msg}']

            if t[1] != 'PRIVMSG':
                raise Exception(f'Invalid ChannelMessage(PRIVMSG), {text!r}')
            # ====USER====
            # t[0] -> ':{user}!{user2?}@{user3?}.{host}'
            # t[0].split('!', 1) -> [':{user}', '{user2?}@{user3?}.{host}']
            # t[0].split('!', 1)[0] -> ':{user}'
            # t[0].split('!', 1)[0][1:] -> '{user}'
            user = t[0].split('!', 1)[0][1:]

            # ===CHANNEL====
            # t[2] -> '#{chan}'
            # t[2][1:] -> '{chan}'
            channel = t[2][1:]

            # ===MESSAGE===
            # t[3] -> ':{msg}'
            # t[3][1:] -> '{msg}'
            text = t[3][1:]

            return ChannelMessage(text=text, user=user, channel=channel)

    def __init__(self, text: str, user: str, channel: str):
        super().__init__(text)
        self._type = 'PRIVMSG'
        self.flags = {}
        self.text: str = text.replace('\r\n', '')
        self.user = user
        self.channel = channel

    def __repr__(self):
        return 'ChannelMessage(text={!r}, user={!r}, channel={!r})'.format(self.text, self.user, self.channel)

    def __str__(self):
        return '#{chan} <{user}> {text}'.format(user=self.user, text=self.text, chan=self.channel)

    def __bytes__(self):
        if self.outgoing:
            return bytes('PRIVMSG #{chan} :{text}\r\n'.format(chan=self.channel, text=self.text), 'utf-8')
        else:
            return b''

    def reply(self, text: str):
        new = ChannelMessage(text=text, user='OUTGOING', channel=self.channel)
        new.outgoing = True
        return new


class PingMessage(Message):
    @staticmethod
    def from_match(m: typing.Match[str]):
        new = PingMessage()
        new.host = m[1]
        return new

    @staticmethod
    def from_text(text):
        new = PingMessage()
        # PING :{host}
        new.host = text.split(' ', 1)[1][1:].replace('\r\n', '')
        return new

    def __init__(self, host: typing.Optional[str] = None):
        self.host = host
        super().__init__(str(self))

    def __repr__(self):
        return 'PingMessage(host={!r})'.format(self.host)

    def __str__(self):
        return 'PING :{}'.format(self.host)

    def reply(self):
        return PongMessage(self.host)


class PongMessage(Message):
    @staticmethod
    def from_match(m: typing.Match[str]):
        return None

    @staticmethod
    def from_text(text):
        return None

    def __init__(self, host):
        super().__init__(host)
        self.host = host

    def __repr__(self):
        return 'PongMessage(host={!r})'.format(self.host)

    def __str__(self):
        return 'PONG :{}'.format(self.host)

    def __bytes__(self):
        return bytes('PONG :{}\r\n'.format(self.host), 'utf-8')

    def reply(self):
        raise RuntimeError('Cannot reply to a PongMessage.')


class NoticeMessage(Message):
    @staticmethod
    def from_match(m: typing.Match[str]):
        new = NoticeMessage('')
        new.message_id = process_twitch_flags(m[1])['msg-id']
        new.host = m[2]
        new.channel = m[3]
        new.text = m[4]
        # @msg-id=%s :tmi.twitch.tv NOTICE #{chan} :{msg}
        return new

    @staticmethod
    def from_text(text):
        m = re.match(irclib.NOTICE_MESSAGE_PATTERN, text)
        if m:
            return NoticeMessage.from_match(m)
        else:
            raise Exception('Invalid NoticeMessage(NOTICE): {!r}'.format(text))

    def __init__(self, text, message_id=None, channel=None, host=None):
        super().__init__(text)
        self.text = text
        self.message_id = message_id
        self.channel = channel
        self.host = host


class JoinMessage(Message):
    @staticmethod
    def from_match(m: typing.Match[str]):
        new = JoinMessage(m[1], m[2])
        return new

    def __init__(self, user: str, channel: str, outgoing=False):
        super().__init__('{} JOIN {}'.format(user, channel))
        self.user = user
        self.channel = channel
        self.outgoing = outgoing

    def __repr__(self) -> str:
        if self.outgoing:
            return f'JoinMessage(user={self.user!r}, channel={self.channel!r}, outgoing=True)>'
        else:
            return f'JoinMessage(user={self.user!r}, channel={self.channel!r})>'

    def __str__(self):
        if self.outgoing:
            return f'JOIN {self.channel}'
        else:
            return f'{self.user} JOIN {self.channel}'

    def __bytes__(self):
        if self.outgoing:
            return bytes(f'JOIN {self.channel}\r\n', 'utf-8')
        else:
            return b''


class PartMessage(Message):
    @staticmethod
    def from_match(m: typing.Match[str]):
        new = PartMessage(m[1], m[2])
        return new

    def __init__(self, user: str, channel: str):
        super().__init__('{} PART {}'.format(user, channel))
        self.user = user
        self.channel = channel

    def __repr__(self):
        if self.outgoing:
            return f'PartMessage(user={self.user!r}, channel={self.channel!r})  # outgoing'
        else:
            return f'PartMessage(user={self.user!r}, channel={self.channel!r})'

    def __str__(self):
        if self.outgoing:
            return f'<PART {self.channel}>'
        else:
            return f'<{self.user} PART {self.channel}>'


MESSAGE_PATTERN_DICT: typing.Dict[str, typing.Union[
    typing.Type[ChannelMessage],
    typing.Type[PingMessage],
    typing.Type[NoticeMessage]]
] = {
    irclib.PRIVMSG_PATTERN_TWITCH: ChannelMessage,
    irclib.PING_MESSAGSE_PATTERN: PingMessage,
    irclib.NOTICE_MESSAGE_PATTERN: NoticeMessage,
    irclib.JOIN_MESSAGE_PATTERN: JoinMessage,
    irclib.PART_MESSAGE_PATTERN: PartMessage
}


def auto_message(message):
    for k, v in MESSAGE_PATTERN_DICT.items():
        m = re.match(k, message)
        if m:
            return v.from_match(m)

    # if nothing matches return generic irc message.
    return Message(message)

    # if re.match(PRIVMSG_PATTERN_TWITCH, message):
    #     return ChannelMessage(message)
    # elif re.match(PING_MESSAGSE_PATTERN, message):
    #     return PingMessage(message)
    # elif re.match(NOTICE_MESSAGE_PATTERN, message):
    #     return NoticeMessage(message)
    # else:
    #     return Message(message)
