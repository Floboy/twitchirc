#  Library to make crating bots for Twitch chat easier.
#  Copyright (c) 2019 Maciej Marciniak
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import typing
import warnings

import twitchirc


class Message:
    @classmethod
    def from_match(cls, m: typing.Match[str]):
        """
        Create a new object using a match

        :param m: Match
        :return: The new object
        """
        warnings.warn(DeprecationWarning('from_match is deprecated'))
        return cls.upgrade(Message.from_text(m.string))

    @classmethod
    def from_text(cls, text: str):
        msg = cls.parse_text(text)
        return cls.upgrade(msg)

    @classmethod
    def _unescape_tag_value(cls, text: str) -> str:
        return (
            text.replace('\:', ';')
                .replace('\\r', '\r')
                .replace('\\n', '\n')
                .replace('\\s', ' ')
                .replace(r'\\', '\\')
        )

    @classmethod
    def _escape_tag_value(cls, text: str) -> str:
        return (
            text.replace(';', '\:')
                .replace(' ', '\s')
                .replace('\r', '\\r')
                .replace('\n', '\\n')
                .replace('\\', '\\\\')
        )

    @classmethod
    def parse_text(cls, text: str):
        """
        Create a new object from text

        :param text: Text to create it from.
        :return: The new object
        """
        # @a=b;c=d :%s!%s@%s PRIVMSG #channel :text
        original_text = text
        prefix = None
        tags = {}
        if text.startswith('@'):
            # msg has tags
            tags_raw, text = text.split(' ', 1)
            tags_raw = tags_raw[1:].split(';')
            for pair in tags_raw:
                k, v = pair.split('=', 1)
                tags[k] = cls._unescape_tag_value(v)

        if text.startswith(':'):
            # message has a prefix
            prefix, text = text.split(' ', 1)
            prefix = prefix[1:]  # remove :

        if ' ' in text:
            command, text = text.split(' ', 1)
            params = []
            words = text.split(' ')
            for i, word in enumerate(words):
                word: str
                if word.startswith(':'):
                    # trailing
                    params.append(' '.join([word[1:]] + words[i + 1:]))
                    break
                else:
                    params.append(word)
        else:
            command = text
            params = []

        return Message(
            params,
            outgoing=False,
            source=prefix,
            action=command,
            parent=None,
            raw_data=original_text,
            flags=tags
        )

    def __init__(self, args: typing.Union[str, typing.List[str]], outgoing=False, source=None, action='', parent=None,
                 raw_data=None,
                 flags: typing.Dict[str, str] = None):
        """
        Message object.

        WARNING: If you receive this object at runtime, that means that, the packet you received is not known to this
        library

        :param args: Text received.
        """
        self.action = action
        self.source = source
        if isinstance(args, list):
            self.new_args: typing.List[str] = args
            self.args = ''
            if args:
                for i, arg in enumerate(args):
                    if i == len(args) - 1:
                        self.args += ':' + arg
                    else:
                        self.args += arg + ' '
                self.args = self.args.rstrip(' ')
        else:
            self.args = args
            self.new_args = args.split(' ')

        self.outgoing = outgoing
        self.parent = parent
        self.raw_data = raw_data
        self.flags = flags or {}

    def __eq__(self, other):
        if isinstance(other, Message):
            return (other.new_args == self.new_args
                    and other.__class__ == self.__class__
                    and other.action == self.action
                    and other.source == self.source)
        else:
            return False

    def __repr__(self):
        if self.source is not None:
            return f'{self.__class__.__name__}(source={self.source!r}, action={self.action!r}, args={self.new_args!r})'
        elif self.args:
            return f'{self.__class__.__name__}(args={self.new_args!r})'
        elif self.raw_data:
            return f'{self.__class__.__name__}(raw_data={self.raw_data!r})'
        else:
            return (f'{self.__class__.__name__}({self.args!r}, source={self.source!r}, action={self.action!r}, '
                    f'raw_data={self.raw_data!r})')

    def __str__(self):
        return f'<Raw IRC message: {self.action} {self.args}>'

    def __bytes__(self):
        output = b''
        if self.flags:
            tags = []
            for k, v in self.flags.items():
                if isinstance(v, str):
                    tags.append(k.encode() + b'=' + Message._escape_tag_value(v).encode())
                # otherwise the tag is considered a way to store additional context information about the msg
            if tags:
                output += b'@' + b';'.join(tags) + b' '

        if self.source and not self.outgoing:  # limitation introduced for backwards compatibility
            output += b':' + self.source.encode() + b' '

        if self.action:
            output += self.action.encode()
        if self.new_args:
            output += b' '  # include a space before the args
            had_trailing = False
            for i, arg in enumerate(self.new_args):
                if ' ' in arg and not had_trailing:
                    had_trailing = True
                    if i == 0:
                        output += b':' + arg.encode()
                    else:
                        output += b' :' + arg.encode()
                else:
                    if i == 0:
                        output += arg.encode()
                    else:
                        output += b' ' + arg.encode()
        output += b'\r\n'
        return output

    @classmethod
    def upgrade(cls, msg: 'Message'):  # -> cls
        return msg

    def _copy_from(self, other: 'Message'):
        self.action = other.action
        self.source = other.source
        self.new_args = other.new_args
        self.args = other.args
        self.outgoing = other.outgoing
        self.parent = other.parent
        self.raw_data = other.raw_data
        self.flags = other.flags

    @property
    def user(self):
        user, _ = self.source.split('!', 1)
        return user


class WhisperMessage(Message):
    @classmethod
    def upgrade(cls, msg: 'Message') -> 'WhisperMessage':
        new = cls(msg.flags, msg.user, '', msg.args, msg.outgoing)
        new._copy_from(msg)
        return new

    def __repr__(self):
        return (f'WhisperMessage(flags={self.flags!r}, user_from={self.user_from!r}, user_to={self.user_to!r}, '
                f'text={self.text!r})')

    def __str__(self):
        return f'{self.user_from} -> {self.user_to}: {self.text}'

    def __bytes__(self):
        if self.outgoing:
            return bytes(f'PRIVMSG #jtv :/w {self.user_to} {self.text}\r\n', 'utf-8')
        else:
            return super().__bytes__()

    def __init__(self, flags, user_from, user_to, text, outgoing=False):
        super().__init__([text], outgoing=outgoing)
        self.text = text
        self.user_to = user_to
        self.user_from = user_from
        self.flags = flags
        self.channel = 'whispers'
        self.action = 'WHISPER'
        self.source = f'{self.user_from}!{self.user_from}@{self.user_from}.tmi.twitch.tv'

    @property
    def user(self):
        return self.user_from

    def reply(self, text: str):
        new = WhisperMessage(flags={}, user_from='OUTGOING', user_to=self.user_from, text=text, outgoing=True)
        return new


class ChannelMessage(Message):
    def moderate(self):
        if self.outgoing:
            raise RuntimeError('Cannot moderate a message that\'s going to be sent.')

        return twitchirc.ModerationContainer.from_message(self, self.parent)

    @classmethod
    def upgrade(cls, msg: 'Message'):
        channel, text = msg.new_args
        new = cls(text, msg.user, channel.lstrip('#'), msg.outgoing, msg.parent)
        new._copy_from(msg)
        return new

    def __init__(self, text: str, user: str, channel: str, outgoing=False, parent=None):
        super().__init__(['#' + channel, text], outgoing=outgoing, parent=parent)
        self.flags = {}
        self.text: str = text.replace('\r\n', '')
        self.source = f'{user}!{user}@{user}.tmi.twitch.tv'
        self.channel = channel
        self.action = 'PRIVMSG'

    def __repr__(self):
        return 'ChannelMessage(text={!r}, user={!r}, channel={!r})'.format(self.text, self.user, self.channel)

    def __str__(self):
        return '#{chan} <{user}> {text}'.format(user=self.user, text=self.text, chan=self.channel)

    def reply(self, text: str, force_slash=False):
        if not force_slash and text.startswith(('.', '/')):
            text = '/ ' + text
        new = ChannelMessage(text=text, user='OUTGOING', channel=self.channel)
        new.outgoing = True
        return new

    def reply_directly(self, text: str):
        new = WhisperMessage(flags={}, user_from='OUTGOING', user_to=self.user, text=text, outgoing=True)
        return new

    # region new_args property
    @property
    def new_args(self):
        return ['#' + self.channel, self.text]

    @new_args.setter
    def new_args(self, value):
        pass
    # endregion


class PingMessage(Message):
    @classmethod
    def upgrade(cls, msg: 'Message'):
        new = cls(msg.args)
        new._copy_from(msg)
        return new

    def __init__(self, host: typing.Optional[str] = None):
        args = [host] if host is not None else []
        super().__init__(args)
        self.outgoing = False
        self.action = 'PING'

    @property
    def host(self):
        if self.new_args:
            return self.new_args[-1]
        else:
            return None

    def __repr__(self):
        return 'PingMessage(host={!r})'.format(self.host)

    def reply(self):
        return PongMessage(self.host)


class PongMessage(Message):
    @classmethod
    def upgrade(cls, msg: 'Message'):
        new = cls(msg.args)
        new._copy_from(msg)
        return new

    def __init__(self, host: typing.Optional[str] = None):
        args = [host] if host is not None else []
        super().__init__(args)
        self.outgoing = True
        self.action = 'PONG'

    @property
    def host(self):
        if self.new_args:
            return self.new_args[-1]
        else:
            return None

    def __repr__(self):
        return 'PongMessage(host={!r})'.format(self.host)

    def reply(self):
        raise RuntimeError('Cannot reply to a PongMessage.')


class NoticeMessage(Message):
    @classmethod
    def upgrade(cls, msg: 'Message'):
        channel, text = msg.args.split(' ', 1)
        new = NoticeMessage(text, msg.flags.get('msg-id'), channel.lstrip('#'))
        new._copy_from(msg)
        return new

    def __init__(self, text, message_id=None, channel=None):
        super().__init__(['#' + channel, text])
        self.text = text
        self.channel = channel
        self.action = 'NOTICE'

    @property
    def message_id(self):
        return self.flags.get('msg-id')


class JoinMessage(Message):
    @classmethod
    def upgrade(cls, msg: 'Message'):
        channel = msg.new_args[0].lstrip('#')
        new = JoinMessage(msg.user, channel, False)
        new._copy_from(msg)
        return new

    def __init__(self, user: str, channel: str, outgoing=False):
        super().__init__('{} JOIN {}'.format(user, channel), outgoing=outgoing)
        self.source = f'{user}!{user}@{user}.tmi.twitch.tv'
        self.channel = channel
        self.action = 'JOIN'

    def __repr__(self) -> str:
        if self.outgoing:
            return f'JoinMessage(user={self.user!r}, channel={self.channel!r}, outgoing=True)'
        else:
            return f'JoinMessage(user={self.user!r}, channel={self.channel!r})'

    def __str__(self):
        if self.outgoing:
            return f'JOIN {self.channel}'
        else:
            return f'{self.user} JOIN {self.channel}'


class PartMessage(Message):
    @classmethod
    def upgrade(cls, msg: 'Message'):
        channel = msg.new_args[0].lstrip('#')
        new = PartMessage(msg.user, channel, False)
        new._copy_from(msg)
        return new

    def __init__(self, user: str, channel: str, outgoing=False):
        super().__init__(f'{user} PART {channel}', outgoing=outgoing)
        self.source = f'{user}!{user}@{user}.tmi.twitch.tv'
        self.channel = channel

    def __repr__(self):
        if self.outgoing:
            return f'PartMessage(user={self.user!r}, channel={self.channel!r}, outgoing=True)'
        else:
            return f'PartMessage(user={self.user!r}, channel={self.channel!r})'

    def __str__(self):
        if self.outgoing:
            return f'<PART {self.channel}>'
        else:
            return f'<{self.user} PART {self.channel}>'


class UsernoticeMessage(Message):
    @classmethod
    def upgrade(cls, msg: 'Message'):
        channel = msg.new_args[0].lstrip('#')
        new = UsernoticeMessage(msg.flags, channel)
        new._copy_from(msg)
        return new

    def __repr__(self):
        return f'UsernoticeMessage(flags={self.flags!r}, channel={self.channel!r})'

    def __str__(self):
        return f'<USERNOTICE {self.channel}>'

    def __init__(self, flags, channel):
        super().__init__('')
        self.flags = flags
        self.channel = channel


class UserstateMessage(Message):
    @classmethod
    def upgrade(cls, msg: 'Message'):
        channel = msg.new_args[0].lstrip('#')
        new = UsernoticeMessage(msg.flags, channel)
        new._copy_from(msg)
        return new

    def __repr__(self):
        return f'UserstateMessage(flags={self.flags!r}, channel={self.channel!r})'

    def __str__(self):
        return f'<USERSTATE {self.channel}>'

    def __init__(self, flags, channel):
        super().__init__('')
        self.flags = flags
        self.channel = channel


class ReconnectMessage(Message):
    @classmethod
    def upgrade(cls, msg: 'Message'):
        new = cls()
        new._copy_from(msg)
        return new

    def __repr__(self):
        return f'ReconnectMessage()'

    def __str__(self):
        return f'<RECONNECT>'

    def __init__(self):
        super().__init__('RECONNECT')


COMMAND_MESSAGE_DICT: typing.Dict[str, typing.Type[Message]] = {
    'PRIVMSG': ChannelMessage,
    'PING': PingMessage,
    'PONG': PongMessage,
    'NOTICE': NoticeMessage,
    'JOIN': JoinMessage,
    'PART': PartMessage,
    'WHISPER': WhisperMessage,
    'RECONNECT': ReconnectMessage,
    'USERNOTICE': UsernoticeMessage,
    'USERSTATE': UserstateMessage
}


def auto_message(message, parent=None):
    msg = Message.from_text(message)
    msg.parent = parent
    for command, klass in COMMAND_MESSAGE_DICT.items():
        if msg.action == command:
            return klass.upgrade(msg)

    # if nothing matches return generic irc message.
    return msg
