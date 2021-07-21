#  Library to make crating bots for Twitch chat easier.
#  Copyright (c) 2021 Mm2PL
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

import unittest

import twitchirc


# noinspection DuplicatedCode
class IrcParsingTests(unittest.TestCase):
    def test_parse_privmsg(self):
        input_str = (
            '@badge-info=subscriber/13;badges=subscriber/12,'
            'glhf-pledge/1;color=#DAA520;display-name=Mm2PL;emotes=;flags=;id=4d18ce89-b62a-4f4e-be71-b432b8dd3f86'
            ';mod=0;room-id=11148817;subscriber=1;tmi-sent-ts=1625487203887;turbo=0;user-id=117691339;user-type= '
            ':mm2pl!mm2pl@mm2pl.tmi.twitch.tv PRIVMSG #pajlada :-tags'
        )
        msg = twitchirc.Message.from_text(input_str)
        self.assertEqual('mm2pl!mm2pl@mm2pl.tmi.twitch.tv', msg.source)
        # noinspection DuplicatedCode
        self.assertEqual('PRIVMSG', msg.action)
        self.assertEqual(False, msg.outgoing)
        self.assertEqual(input_str, msg.raw_data)
        self.assertEqual('#pajlada :-tags', msg.args)
        self.assertEqual(['#pajlada', '-tags'], msg.new_args)
        self.assertEqual({
            "badge-info": "subscriber/13",
            "badges": "subscriber/12,glhf-pledge/1",
            "color": "#DAA520",
            "display-name": "Mm2PL",
            "emotes": "",
            "flags": "",
            "id": "4d18ce89-b62a-4f4e-be71-b432b8dd3f86",
            "mod": "0",
            "room-id": "11148817",
            "subscriber": "1",
            "tmi-sent-ts": "1625487203887",
            "turbo": "0",
            "user-id": "117691339",
            "user-type": ""
        }, msg.flags)

        msg2 = twitchirc.ChannelMessage.upgrade(msg)
        # noinspection DuplicatedCode
        self.assertEqual('mm2pl!mm2pl@mm2pl.tmi.twitch.tv', msg2.source)
        self.assertEqual('PRIVMSG', msg2.action)
        self.assertEqual(False, msg2.outgoing)
        self.assertEqual(input_str, msg2.raw_data)
        self.assertEqual('#pajlada :-tags', msg2.args)
        self.assertEqual(['#pajlada', '-tags'], msg2.new_args)
        self.assertEqual({
            "badge-info": "subscriber/13",
            "badges": "subscriber/12,glhf-pledge/1",
            "color": "#DAA520",
            "display-name": "Mm2PL",
            "emotes": "",
            "flags": "",
            "id": "4d18ce89-b62a-4f4e-be71-b432b8dd3f86",
            "mod": "0",
            "room-id": "11148817",
            "subscriber": "1",
            "tmi-sent-ts": "1625487203887",
            "turbo": "0",
            "user-id": "117691339",
            "user-type": ""
        }, msg2.flags)

    def test_parse_join(self):
        input_str = (
            ':mm2pl!mm2pl@mm2pl.tmi.twitch.tv JOIN #pajlada'
        )
        msg = twitchirc.Message.from_text(input_str)
        self.assertEqual(msg.source, 'mm2pl!mm2pl@mm2pl.tmi.twitch.tv')
        self.assertEqual(msg.action, 'JOIN')
        self.assertEqual(msg.outgoing, False)
        self.assertEqual(msg.raw_data, input_str)
        self.assertEqual(msg.args, ':#pajlada')
        self.assertEqual(msg.new_args, ['#pajlada'])
        self.assertEqual(msg.flags, {})

        msg2 = twitchirc.JoinMessage.upgrade(msg)
        self.assertEqual(msg2.source, 'mm2pl!mm2pl@mm2pl.tmi.twitch.tv')
        # noinspection DuplicatedCode
        self.assertEqual(msg2.action, 'JOIN')
        self.assertEqual(msg2.outgoing, False)
        self.assertEqual(msg2.raw_data, input_str)
        self.assertEqual(msg2.args, ':#pajlada')
        self.assertEqual(msg2.new_args, ['#pajlada'])
        self.assertEqual(msg2.flags, {})

    def test_parse_part(self):
        input_str = (
            ':justinfan1234!justinfan1234@justinfan1234.tmi.twitch.tv PART #mm2pl'
        )
        msg = twitchirc.auto_message(input_str)

        self.assertTrue(isinstance(msg, twitchirc.PartMessage), f'bad automsg')
        self.assertEqual('justinfan1234!justinfan1234@justinfan1234.tmi.twitch.tv', msg.source)
        self.assertEqual('PART', msg.action)
        self.assertEqual(False, msg.outgoing)
        self.assertEqual(input_str, msg.raw_data)
        self.assertEqual(':#mm2pl', msg.args)
        self.assertEqual(['#mm2pl'], msg.new_args)
        self.assertEqual({}, msg.flags)

    def test_automsg_parse_privmsg(self):
        input_str = (
            '@badge-info=subscriber/13;badges=subscriber/12,'
            'glhf-pledge/1;color=#DAA520;display-name=Mm2PL;emotes=;flags=;id=4d18ce89-b62a-4f4e-be71-b432b8dd3f86'
            ';mod=0;room-id=11148817;subscriber=1;tmi-sent-ts=1625487203887;turbo=0;user-id=117691339;user-type= '
            ':mm2pl!mm2pl@mm2pl.tmi.twitch.tv PRIVMSG #pajlada :-tags'
        )
        msg = twitchirc.auto_message(input_str)
        # noinspection DuplicatedCode
        self.assertEqual('mm2pl!mm2pl@mm2pl.tmi.twitch.tv', msg.source)
        self.assertEqual('PRIVMSG', msg.action)
        self.assertEqual(False, msg.outgoing)
        self.assertEqual(input_str, msg.raw_data)
        self.assertEqual('#pajlada :-tags', msg.args)
        self.assertEqual(['#pajlada', '-tags'], msg.new_args)
        self.assertEqual({
            "badge-info": "subscriber/13",
            "badges": "subscriber/12,glhf-pledge/1",
            "color": "#DAA520",
            "display-name": "Mm2PL",
            "emotes": "",
            "flags": "",
            "id": "4d18ce89-b62a-4f4e-be71-b432b8dd3f86",
            "mod": "0",
            "room-id": "11148817",
            "subscriber": "1",
            "tmi-sent-ts": "1625487203887",
            "turbo": "0",
            "user-id": "117691339",
            "user-type": ""
        }, msg.flags)

    def test_parse_ping(self):
        input_str = (
            'PING :tmi.twitch.tv'
        )
        msg = twitchirc.auto_message(input_str)

        self.assertTrue(isinstance(msg, twitchirc.PingMessage), 'bad automsg')
        self.assertEqual(None, msg.source)
        self.assertEqual('PING', msg.action)
        self.assertEqual(False, msg.outgoing)
        self.assertEqual(input_str, msg.raw_data)
        self.assertEqual(':tmi.twitch.tv', msg.args)
        self.assertEqual(['tmi.twitch.tv'], msg.new_args)
        self.assertEqual({}, msg.flags)

    def test_parse_pong(self):
        input_str = (
            'PONG :tmi.twitch.tv'
        )
        msg = twitchirc.auto_message(input_str)

        self.assertTrue(isinstance(msg, twitchirc.PongMessage), f'bad automsg')
        self.assertEqual(None, msg.source)
        self.assertEqual('PONG', msg.action)
        self.assertEqual(False, msg.outgoing)
        self.assertEqual(input_str, msg.raw_data)
        self.assertEqual(':tmi.twitch.tv', msg.args)
        self.assertEqual(['tmi.twitch.tv'], msg.new_args)
        self.assertEqual({}, msg.flags)

    def test_parse_unknown(self):
        input_str = (
            'UNKNOWNCMD justinfan1234 :these are some args'
        )
        msg = twitchirc.auto_message(input_str)
        self.assertTrue(msg.__class__ == twitchirc.Message, 'bad automsg')
        self.assertEqual(None, msg.source)
        self.assertEqual('UNKNOWNCMD', msg.action)
        self.assertEqual(False, msg.outgoing)
        self.assertEqual(input_str, msg.raw_data)
        self.assertEqual('justinfan1234 :these are some args', msg.args)
        self.assertEqual(['justinfan1234', 'these are some args'], msg.new_args)
        self.assertEqual({}, msg.flags)

    def test_parse_notice(self):
        input_str = (
            '@msg-id=slow_on :tmi.twitch.tv NOTICE #mm2pl :This room is now in slow mode. You may send messages every '
            '10 seconds.'
        )
        msg = twitchirc.auto_message(input_str)

        self.assertTrue(isinstance(msg, twitchirc.NoticeMessage), f'bad automsg')
        self.assertEqual('tmi.twitch.tv', msg.source)
        self.assertEqual('NOTICE', msg.action)
        self.assertEqual(False, msg.outgoing)
        self.assertEqual(input_str, msg.raw_data)
        self.assertEqual('#mm2pl :This room is now in slow mode. You may send messages every 10 seconds.', msg.args)
        self.assertEqual(['#mm2pl', 'This room is now in slow mode. You may send messages every 10 seconds.'],
                         msg.new_args)
        self.assertEqual({'msg-id': 'slow_on'}, msg.flags)
        self.assertEqual('slow_on', msg.message_id)

    def test_parse_usernotice(self):
        input_str = (
            '@badge-info=subscriber/0;badges=subscriber/0,'
            'turbo/1;color=#E88911;display-name=some_user;emotes=;flags=;id=596ef165-6af4-4f08-acde-b6c72ee50c37;'
            'login=some_user;mod=0;msg-id=sub;msg-param-cumulative-months=1;msg-param-months=0;msg-param'
            '-multimonth-duration=1;msg-param-multimonth-tenure=0;msg-param-should-share-streak=0;msg-param-sub-plan'
            '-name=look\sat\sthose\sshitty\semotes,\srip\s$5\sLUL;msg-param-sub-plan=1000;msg-param-was-gifted=false;'
            'room-id=11148817;subscriber=1;system-msg=some_user\ssubscribed\sat\sTier\s1.;'
            'tmi-sent-ts=1626800016285;user-id=493534660;user-type= '
            ':tmi.twitch.tv USERNOTICE #pajlada'
        )
        msg = twitchirc.auto_message(input_str)

        self.assertTrue(isinstance(msg, twitchirc.UsernoticeMessage), f'bad automsg')
        self.assertEqual('tmi.twitch.tv', msg.source)
        self.assertEqual('USERNOTICE', msg.action)
        self.assertEqual(False, msg.outgoing)
        self.assertEqual(input_str, msg.raw_data)
        self.assertEqual(':#pajlada', msg.args)
        self.assertEqual(['#pajlada'], msg.new_args)
        expected = {
            'badge-info': 'subscriber/0',
            'badges': 'subscriber/0,turbo/1',
            'color': '#E88911',
            'display-name': 'some_user',
            'emotes': '',
            'flags': '',
            'id': '596ef165-6af4-4f08-acde-b6c72ee50c37',
            'login': 'some_user',
            'mod': '0',
            'msg-id': 'sub',
            'msg-param-cumulative-months': '1',
            'msg-param-months': '0',
            'msg-param-multimonth-duration': '1',
            'msg-param-multimonth-tenure': '0',
            'msg-param-should-share-streak': '0',
            'msg-param-sub-plan-name': 'look at those shitty emotes, rip $5 LUL',
            'msg-param-sub-plan': '1000',
            'msg-param-was-gifted': 'false',
            'room-id': '11148817',
            'subscriber': '1',
            'system-msg': 'some_user subscribed at Tier 1.',
            'tmi-sent-ts': '1626800016285',
            'user-id': '493534660',
            'user-type': ''
        }
        covered = set()
        for k, v in msg.flags.items():
            self.assertEqual(expected[k], v, f'bad {k} value')
            covered.add(k)
        self.assertEqual(covered, set(expected.keys()))

    def test_parse_escaped_tags(self):
        input_str = (
            r'@key=\\.\:\r\n\svalue UNKNOWNCMD'
        )
        msg = twitchirc.auto_message(input_str)
        self.assertTrue(msg.__class__ == twitchirc.Message, 'bad automsg')
        self.assertEqual(None, msg.source)
        self.assertEqual('UNKNOWNCMD', msg.action)
        self.assertEqual(False, msg.outgoing)
        self.assertEqual(input_str, msg.raw_data)
        self.assertEqual('', msg.args)
        self.assertEqual([], msg.new_args)
        self.assertEqual({
            'key': '\\.;\r\n value'
        }, msg.flags)


# noinspection DuplicatedCode
class IrcComposeTests(unittest.TestCase):
    def test_compose_privmsg_raw(self):
        msg = twitchirc.Message('#test :Testing123 456', True, action='PRIVMSG')
        self.assertEqual(b'PRIVMSG #test :Testing123 456\r\n', bytes(msg))

    def test_compose_multiword_single_arg(self):
        msg = twitchirc.Message(['word word word'], True, action='TEST')
        self.assertEqual(b'TEST :word word word\r\n', bytes(msg))

    def test_compose_privmsg(self):
        msg = twitchirc.ChannelMessage('Testing123 456', 'OUTGOING', 'test', outgoing=True)
        self.assertEqual(b'PRIVMSG #test :Testing123 456\r\n', bytes(msg))

    def test_compose_via_reply_to_privmsg(self):
        orig = twitchirc.ChannelMessage('original', 'some_user', 'some_channel')
        msg = orig.reply('Here is some text')
        self.assertEqual('OUTGOING!OUTGOING@OUTGOING.tmi.twitch.tv', msg.source)
        self.assertEqual('PRIVMSG', msg.action)
        self.assertEqual(True, msg.outgoing)
        self.assertEqual(None, msg.raw_data)
        self.assertEqual('#some_channel :Here is some text', msg.args)
        self.assertEqual(['#some_channel', 'Here is some text'], msg.new_args)
        self.assertEqual({}, msg.flags)

        orig = twitchirc.ChannelMessage('original', 'some_user', 'some_channel')
        msg = orig.reply('/help')
        self.assertEqual('OUTGOING!OUTGOING@OUTGOING.tmi.twitch.tv', msg.source)
        self.assertEqual('PRIVMSG', msg.action)
        self.assertEqual(True, msg.outgoing)
        self.assertEqual(None, msg.raw_data)
        self.assertEqual('#some_channel :/ /help', msg.args)
        self.assertEqual(['#some_channel', '/ /help'], msg.new_args)
        self.assertEqual({}, msg.flags)

        orig = twitchirc.ChannelMessage('original', 'some_user', 'some_channel')
        msg = orig.reply('/help', True)
        self.assertEqual('OUTGOING!OUTGOING@OUTGOING.tmi.twitch.tv', msg.source)
        self.assertEqual('PRIVMSG', msg.action)
        self.assertEqual(True, msg.outgoing)
        self.assertEqual(None, msg.raw_data)
        self.assertEqual('#some_channel :/help', msg.args)
        self.assertEqual(['#some_channel', '/help'], msg.new_args)
        self.assertEqual({}, msg.flags)

    def test_compose_whisper_via_reply_to_privmsg(self):
        orig = twitchirc.ChannelMessage('original', 'some_user', 'some_channel')
        msg = orig.reply_directly('Here is some text')
        self.assertEqual('OUTGOING!OUTGOING@OUTGOING.tmi.twitch.tv', msg.source)
        self.assertEqual('WHISPER', msg.action)
        self.assertEqual(True, msg.outgoing)
        self.assertEqual(None, msg.raw_data)
        self.assertEqual(':Here is some text', msg.args)
        self.assertEqual(['Here is some text'], msg.new_args)
        self.assertEqual(b'PRIVMSG #jtv :/w some_user Here is some text\r\n', bytes(msg))
        self.assertEqual({}, msg.flags)

    def test_compose_whisper_directly(self):
        msg = twitchirc.WhisperMessage({}, 'OUTGOING', 'some_user', 'Here is some text', outgoing=True)
        self.assertEqual('OUTGOING!OUTGOING@OUTGOING.tmi.twitch.tv', msg.source)
        self.assertEqual('WHISPER', msg.action)
        self.assertEqual(True, msg.outgoing)
        self.assertEqual(None, msg.raw_data)
        self.assertEqual(':Here is some text', msg.args)
        self.assertEqual(['Here is some text'], msg.new_args)
        self.assertEqual(b'PRIVMSG #jtv :/w some_user Here is some text\r\n', bytes(msg))
        self.assertEqual({}, msg.flags)

    # noinspection PyMethodMayBeStatic
    def test_compose_ping_msg(self):
        twitchirc.PingMessage('tmi.twitch.tv')
        twitchirc.PingMessage()

    def test_compose_pong_msg(self):
        orig1 = twitchirc.PingMessage('tmi.twitch.tv')
        msg = orig1.reply()
        self.assertEqual(None, msg.source)
        self.assertEqual('PONG', msg.action)
        self.assertEqual(True, msg.outgoing)
        self.assertEqual(None, msg.raw_data)
        self.assertEqual(':tmi.twitch.tv', msg.args)
        self.assertEqual(['tmi.twitch.tv'], msg.new_args)
        self.assertEqual(b'PONG tmi.twitch.tv\r\n', bytes(msg))
        self.assertEqual({}, msg.flags)

        orig2 = twitchirc.PingMessage()
        msg = orig2.reply()
        self.assertEqual(None, msg.source)
        self.assertEqual('PONG', msg.action)
        self.assertEqual(True, msg.outgoing)
        self.assertEqual(None, msg.raw_data)
        self.assertEqual('', msg.args)
        self.assertEqual([], msg.new_args)
        self.assertEqual(b'PONG\r\n', bytes(msg))
        self.assertEqual({}, msg.flags)


class IrcMiscTests(unittest.TestCase):
    def test_complex_recode(self):
        orig = twitchirc.auto_message(
            '@badge-info=subscriber/13;badges=subscriber/12,'
            'glhf-pledge/1;color=#DAA520;display-name=Mm2PL;emotes=;flags=;id=4d18ce89-b62a-4f4e-be71-b432b8dd3f86'
            ';mod=0;room-id=11148817;subscriber=1;tmi-sent-ts=1625487203887;turbo=0;user-id=117691339;user-type= '
            ':mm2pl!mm2pl@mm2pl.tmi.twitch.tv PRIVMSG #pajlada :this is a message with spaces'
        )

        line = bytes(orig).decode().strip('\r\n')
        self.assertEqual(orig.raw_data, line)
        self.assertEqual(orig, twitchirc.auto_message(line))


if __name__ == '__main__':
    unittest.main()
