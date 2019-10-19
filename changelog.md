# Version 1.3
 - Added secure option to [`Connection`](twitchirc/twitchirc/connection.py).
 - Added [`RECONNECT_MESSAGE_PATTERN`](twitchirc/twitchirc/patterns.py) and [`ReconnectionMessage`](twitchirc/twitchirc/messages.py#L371).
 - Implemented automatic reconnection in `Bot`, [here](twitchirc/twitchirc/bot.py#L299) and [here](twitchirc/twitchirc/bot.py#L321)
 - Added automatic escaping of `/` and `.` to [`ChannelMessage.reply`](twitchirc/twitchirc/messages.py#L185)
 
# Version 1.2
 - Add docstrings to messages.py.
 - Changed repr of Message.
 - Added WhisperMessage.
 - Added a scheduler to Bot.
 - Added matcher_function field to Command.
 - Fixed a bug in Connection.__init__ not registering the atexit close handler. 
 - Changed regexes.
# Version 1.1
 - changed version number to 1.1,
 - added required_permissions to Bot.add_command,
 - fixed a minor comment mistake (Bot line 129),
 - changed Bot.send() to automatically pick the queue,
 - changed docstrings in connection.py,
 - tweaked some regexps,
 - added the GlobalNoticeMessage and UsernoticeMessage classes (UsernoticeMessage has not pattern attached to it),
 - removed some commented-out code,
 - added `__dict__` to PermissionList,
 - changed all stock commands to use the required_permissions argument in bot.add_command, instead of twitchirc.require_permission
