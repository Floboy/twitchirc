import atexit
import typing

import irclib  # Import self.


class Bot(irclib.Connection):
    def run_commands_from_file(self, file_object):
        lines = file_object.readlines()
        user = 'rcfile'
        channel = 'rcfile'
        for num, i in enumerate(lines):
            if i.startswith('@'):
                if i.startswith('@at'):
                    channel = i.replace('@at ', '')
                elif i.startswith('@as'):
                    user = i.replace('@as ', '')
                continue
            m = irclib.ChannelMessage(user=user, channel=channel, text=i.replace('\n', ''))
            m.flags = {
                'badge-info': '',
                'badges': 'moderator/1',
                'display-name': 'RCFile',
                'id': '00000000-0000-0000-0000-{:0>12}'.format(num),
                'user-id': 'rcfile',
                'emotes': ''
            }
            self._call_command_handlers(m)

    def __init__(self, address, username: str, password: typing.Union[str, None] = None, port: int = 6667,
                 no_connect=False, storage=None, no_atexit=False):
        """
        A bot class.

        :param address: Address to connect to
        :param username: Username to use
        :param password: Password if needed.
        :param port: Irc port.
        :param no_connect: Don't connect to the chat straight away
        :param storage: irclib.Storage compatible object to use as the storage.
        """
        super().__init__(address, port, no_atexit=True)
        if not no_connect:
            self.connect(username, password)
        self.username = username
        self._password = password
        self.commands: typing.List[irclib.Command] = []
        self.handlers: typing.Dict[str, typing.List[typing.Callable]] = {
            'pre_disconnect': [],
            'post_disconnect': [],
            'pre_save': [],
            'post_save': [],
            'start': [],
            'recv_join_msg': [],
            'recv_part_msg': [],
            'recv_ping_msg': [],
            'permission_error': [],
            'any_msg': [],
            'chat_msg': []
        }
        """
        A dict of handlers

        Available handlers:

        * pre_disconnect, args: ()
        * post_disconnect, args: ()
        * pre_save, args: ()
        * post_save, args: ()
        * start, args: ()
        * permission_error, args: (message, command, missing_permissions)
          -> message the ChannelMessage during which this permission_error was triggered.
          -> command the Command object that triggered it.
             WARN: `command` can be None if `check_permissions` was called (not `check_permissions_from_command`).
          -> missing_permissions permissions that are missing to run the command.
        * any_msg, args: (message)
        * chat_msg, args: (message)
        """

        self.prefix = '!'
        self.storage = storage
        self.on_unknown_command = 'ignore'
        """
        Action to take when an unknown command is encountered.
        Warning: This doesn't apply to commands with a forced prefix.

        Available handlers:

        * ignore - ignore it (default)
        * warn - print a warning to stdout
        * chat_message - send a chat message saying that the command is invalid.
        """
        self.permissions = irclib.PermissionList()
        if no_atexit:
            @atexit.register
            def close_self():
                try:
                    self.stop()
                except:
                    pass

    def add_command(self, command: str,
                    forced_prefix: typing.Optional[str] = None,
                    enable_local_bypass: bool = True) -> typing.Callable[[typing.Callable[[irclib.ChannelMessage],
                                                                                          typing.Any]], irclib.Command]:
        # Im sorry if you are reading this definition
        # here's a better version
        #  -> ((typing.ChannelMessage) -> Any) -> Command
        """
        Add a command to the bot.
        This function is a decorator.

        :param command: Command to be registered.
        :param forced_prefix: Force a prefix to on this command. This is useful when you can change the prefix in the bot.
        :param enable_local_bypass: If False this function will ignore the permissions `irclib.bypass.permission.local.*`. This is useful when creating a command that can change global settings.
        :return: The `function` parameter. This is for using this as a decorator.
        """

        def decorator(func: typing.Callable) -> irclib.Command:
            cmd = irclib.Command(chat_command=command,
                                 function=func, forced_prefix=forced_prefix, parent=self,
                                 enable_local_bypass=enable_local_bypass)
            self.commands.append(cmd)
            return cmd

        return decorator

    def check_permissions(self, message: irclib.ChannelMessage, permissions: typing.List[str],
                          enable_local_bypass=True):
        """
        Check if the user has the required permissions to run a command

        :param message: Message received.
        :param permissions: Permissions required.
        :param enable_local_bypass: If False this function will ignore the permissions `irclib.bypass.permission.local.*`. This is useful when creating a command that can change global settings.
        :return: A list of missing permissions.

        NOTE `permission_error` handlers are called if this function would return a non empty list.
        """
        missing_permissions = []
        if message.user not in self.permissions:
            missing_permissions = permissions
        else:
            perms = self.permissions.get_permission_state(message)
            if irclib.GLOBAL_BYPASS_PERMISSION in perms or \
                    (enable_local_bypass and irclib.LOCAL_BYPASS_PERMISSION_TEMPLATE.format(message.channel) in perms):
                return []
            for p in permissions:
                if p not in perms:
                    missing_permissions.append(p)
        if missing_permissions:
            self.call_handlers('permission_error', message, None, missing_permissions)
        return missing_permissions

    def check_permissions_from_command(self, message: irclib.ChannelMessage,
                                       command: irclib.Command):
        """
        Check if the user has the required permissions to run a command

        :param message: Message received.
        :param command: Command used.
        :return: A list of missing permissions.

        NOTE `permission_error` handlers are called if this function would return a non empty list.
        """
        missing_permissions = []
        if message.user not in self.permissions:
            missing_permissions = command.permissions_required
        else:
            perms = self.permissions.get_permission_state(message)
            if irclib.GLOBAL_BYPASS_PERMISSION in perms or \
                    (
                            command.enable_local_bypass
                            and (irclib.LOCAL_BYPASS_PERMISSION_TEMPLATE.format(message.channel) in perms)
                    ):
                return []
            for p in command.permissions_required:
                if p not in perms:
                    missing_permissions.append(p)
        if missing_permissions:
            self.call_handlers('permission_error', message, command, missing_permissions)
        return missing_permissions

    def _call_command_handlers(self, message: irclib.ChannelMessage):
        if message.text.startswith(self.prefix):
            was_handled = False
            if ' ' not in message.text:
                message.text += ' '
            for handler in self.commands:
                if message.text.startswith(self.prefix + handler.ef_command):
                    handler(message)
                    was_handled = True
            if not was_handled:
                if self.on_unknown_command == 'warn':
                    irclib.warn(f'Unknown command {message!r}')
                elif self.on_unknown_command == 'chat_message':
                    msg = message.reply(f'Unknown command {message.text.split(" ", 1)[0]!r}')
                    self.send(msg, msg.channel)
                elif self.on_unknown_command == 'ignore':
                    # Just ignore it.
                    pass
                else:
                    raise Exception('Invalid handler in `on_unknown_command`. Valid options: warn, chat_message, '
                                    'ignore.')
        else:
            for handler in self.commands:
                if handler.forced_prefix is None:
                    continue
                elif message.text.startswith(handler.ef_command):
                    handler(message)

    def run(self):
        try:
            self._run()
        except KeyboardInterrupt:
            print('Got SIGINT, exiting.')
            self.stop()
            return

    def _run(self):
        if self.socket is None:
            self.connect(self.username, self._password)
        self.hold_send = False
        self.call_handlers('start')
        while 1:
            if self.socket is None:  # self.disconnect() was called.
                break
            irclib.info('Receiving.')
            self.receive()
            irclib.info('Processing.')
            self.process_messages(100, mode=2)  # process all the messages.
            irclib.info('Calling handlers.')
            for i in self.receive_queue.copy():
                irclib.info('<', repr(i))
                self.call_handlers('any_msg', i)
                if isinstance(i, irclib.PingMessage):
                    self.force_send('PONG {}\r\n'.format(i.host))
                    continue
                elif isinstance(i, irclib.ChannelMessage):
                    self.call_handlers('chat_msg', i)
                    self._call_command_handlers(i)
                if i in self.receive_queue:  # this check may fail if self.part() was called.
                    self.receive_queue.remove(i)
            if not self.channels_connected:  # if the bot left every channel, stop processing messages.
                break
            self.flush_queue(max_messages=100)

    def call_handlers(self, event, *args):
        if event not in ['any_msg', 'chat_msg']:
            irclib.info(f'Calling handlers for event {event!r} with args {args!r}')
        for h in self.handlers[event]:
            h(event, *args)

    def disconnect(self):
        self.call_handlers('pre_disconnect')
        super().disconnect()
        self.call_handlers('post_disconnect')

    def stop(self):
        self.call_handlers('pre_save')
        self.storage.save(is_auto_save=False)
        self.call_handlers('post_save')
        self.disconnect()
