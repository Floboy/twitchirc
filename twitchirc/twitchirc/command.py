import typing

import twitchirc

Bot = typing.TypeVar('Bot')


class Command:
    def __init__(self, chat_command: str, function: typing.Callable, parent: Bot,
                 forced_prefix: typing.Optional[str] = None, enable_local_bypass: bool = True):
        self.enable_local_bypass = enable_local_bypass
        self.ef_command = (forced_prefix + chat_command + ' ') if forced_prefix is not None else chat_command + ' '
        self.chat_command = chat_command
        self.function = function
        self.permissions_required = []
        self.forced_prefix = forced_prefix
        self.parent = parent

    def __call__(self, message: twitchirc.ChannelMessage):
        if self.permissions_required:
            o = self.parent.check_permissions_from_command(message, self)
            if o:  # a non empty list of missing permissions.
                return
        self.function(message)
