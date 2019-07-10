# TwitchIRC

An unofficial library for the Twitch chat. Written in pure Python 3.6

## Features

- Easy to use
- Little to no manual processing of the IRC protocol
- Builtin permission system
- Automatically saving storage (currently JSON only)
- Lets you process unknown messages however you like
- builtin `Bot` object to simplify making bots

## Example bot
```python
import twitchirc

bot = twitchirc.Bot(username='Your_user_name',
                    password='YOUR_OAUTH_TOKEN', address='irc.chat.twitch.tv')


# create the bot. This will connect you to the Twitch IRC

@bot.add_command('test')
def command_test(msg: twitchirc.ChannelMessage):
    bot.send(msg.reply(f'@{msg.user} on #{msg.channel} with the message: '
                       f'{msg.text!r}. This is a test'))
    # reply to the command.



bot.join(bot.username)  # Make the bot join the its own channel.
bot.permissions.update({
    'your_name_here': [twitchirc.GLOBAL_BYPASS_PERMISSION]
})
# add the bypass permission to your account so you can execute any command.

twitchirc.get_quit_command(bot)  # Add a !quit command to the bot.
bot.run()  # Loop forever, receive commands and execute them.

```

[Changelog](changelog.md)