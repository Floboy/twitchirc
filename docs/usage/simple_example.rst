Simple example
==============
This file shows how to use `twitchirc`.

Code:

.. code-block:: python

    import twitchirc

    bot = twitchirc.Bot('irc.chat.twitch.tv', port=6697, secure=True,
                        username='my_user_name',
                        password='oauth:token')
    bot.prefix = '!'


    @bot.add_command('hi')
    def command_hi(msg: twitchirc.ChannelMessage):
        bot.send(msg.reply(f'@{msg.user}, Hi :)'))


    bot.join(bot.username)
    bot.run()


Explanation:

.. code-block:: python

    import twitchirc

    bot = twitchirc.Bot('irc.chat.twitch.tv', port=6697, secure=True,
                        username='my_user_name',
                        password='oauth:token')
    bot.prefix = '!'

Import `twitchirc`. And then create a bot instance that will use the specified username and password to connect.
Explicitly define the bot's prefix.

.. code-block:: python

    @bot.add_command('hi')
    def command_hi(msg: twitchirc.ChannelMessage):
        bot.send(msg.reply(f'@{msg.user}, Hi :)'))

Define a simple command that just returns '@[USER], Hi :)'.

.. code-block:: python

    bot.join(bot.username)
    bot.run()

Join the bot's channel and start responding to commands.
