# Version 1.8.2
 - minor: add support for sending reply threads

# Version 1.8.1
 - fix: whispers

# Version 1.8.0
 - major: rewrote the entire IRC parser
 - major: added tests

# Version 1.7.8
 - major fix: `channels_connected` will now have channels removed from it and no duplicates should be generated

# Version 1.7.7
 - minor: Reformat moderation.py
 - minor: Add a missing pair of parenthesis

# Version 1.7.6
 - Fix bug to do with duplicate messages.

# Version 1.7.5
 - Make avoiding duplicate messages work. Currently cannot disable this functionality or change the character.

# Version 1.7.4
 - smol bugfix

# Version 1.7.3
 - fix spam reconnect bug

# Version 1.7.1
 - addition: whisper commands
 - minor fix: Make all `Message`s be imported into `__init__`
 - minor addition: new `available_in_whispers` parameter for the `Command` constructor and for `Bot.add_command()`
 - minor addition: `WhisperMessage`s will now "quack" like `ChannelMessage`s, added `channel`, `user` properties

# Version 1.7
 - minor change: `_arun` will now `await asyncio.sleep(0)` to give control to tasks in the background
 - minor change: username and password will now be stored in memory when calling `Connection.login()`
 - minor change: change a couple type hints
 - minor addition: new `clone()` and `clone_and_send_batch()` methods in `Connection`
 - minor addition: new `raw_data` field in all `Message`s that stores the raw data received from the server
 - minor change: better `__repr__` for `Message`
 - minor change: delete old parsing code.
 - major addition: new `UserstateMessage`

# Version 1.6
 - major change: better reconnecting,
 - minor addition: you can now return lists from commands, any object that can be sent will be,
 - minor addition: new 'reconnect' middleware action, called when reconnecting,
 - major change: `AbstractMiddleware` now doesn't inherit from `abc.ABC`, to make it easier to add new events,
 - minor fix: `ModerationContainer.format_channel_mode()` crashed when run, now it doesn't,
 - minor addition: new `moderate()` method for `Connection`s and `Bot`s,
 - minor change: `ModerationContainer`s can now not target a user and message,
 - minor fix: `ModerationContainer.timeout()` now supports an `int` as the timeout length.

# Version 1.5
 - major addition: async support,
 - major addition: allow returning values from commands to send them,
 - major addition: simple moderation features,
 - minor addition: messages now have a link to the connection they came through,
 - minor change: middleware will now ignore unknown events
 
# Version 1.4
 - major addition: docs,
 - major addition: middleware,
 - minor: logging changes
 - major: changes in how Message s work.
 - minor: patterns in MESSAGE_PATTERN_DICT are now compiled.
 - minor: add shell.py a simple module to make experimenting easier.

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
 - Fixed a bug in `Connection.__init__` not registering the atexit close handler. 
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
