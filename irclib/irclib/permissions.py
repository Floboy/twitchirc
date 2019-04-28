import typing

import irclib


def require_permission(permission: str):
    """
    Make the command require a permission.

    Warning: This is a decorator.

    :param permission: The permission
    """

    def decorator(func: irclib.Command) -> irclib.Command:
        if isinstance(func, irclib.Command):
            func.permissions_required.append(permission)
            return func
        else:
            raise Exception(f'Cannot call require_permission on object of type {type(func)!r}.')

    return decorator


def auto_group(message: irclib.ChannelMessage) -> str:
    """
    Get the user's group. This uses the Twitch badges.

    :param message: A message that was sent by the user.
    :return: group name
    """
    group = 'default'
    badges: typing.List[str] = message.flags['badges']
    if 'global_mod/1' in badges:
        return 'global_moderator'
    if 'staff/1' in badges:
        return 'staff'
    if 'broadcaster/1' in badges:
        return 'broadcaster'
    if 'moderator/1' in badges:
        return 'moderator'
    for i in badges:
        if i.startswith('subscriber'):
            group = 'subscriber'
    return group


class PermissionList:
    def __init__(self):
        self.users = {

        }
        self.groups = {
            'default': [

            ],
            'moderator': [
                irclib.GROUP_PARENT.format('default')
                # 'parent.default'
            ],
            'subscriber': [
                irclib.GROUP_PARENT.format('default')
            ],
            'staff': [
                irclib.GROUP_PARENT.format('admin')
            ],
            'global_moderator': [
                irclib.GROUP_PARENT.format('moderator'),
                # 'parent.moderator',
                irclib.GLOBAL_BYPASS_PERMISSION
            ],
            'vip': [
                irclib.GROUP_PARENT.format('default')
                # 'parent.default'
            ],
            'broadcaster': [
                irclib.GROUP_PARENT.format('moderator')
                # 'parent.moderator'
            ],
            'admin': [
                irclib.GROUP_PARENT.format('global_moderator')
                # 'parent.global_moderator'
            ],
            'bot_admin': [
                irclib.GROUP_PARENT.format('staff')
                # 'parent.staff'
            ]
        }
        # DEFAULT
        # |
        # +-- moderator LOCAL_BYPASS
        # |   |
        # |   +-- global_moderator BYPASS
        # |   |   |
        # |   |   +-- admin BYPASS
        # |   |       |
        # |   |       +-- staff BYPASS
        # |   |           |
        # |   |           +-- bot_admin BYPASS
        # |   |
        # |   +-- broadcaster LOCAL_BYPASS
        # |
        # +-- subscriber
        # |
        # +-- vip

    def _get_permissions_from_parents(self, permissions: typing.List[str]):
        permissions = permissions.copy()
        while 1:
            was_extended = False
            for i in permissions.copy():
                if i.startswith('parent.'):
                    permissions.remove(i)
                    permissions.extend(self.groups[i.replace('parent.', '')])
                    was_extended = True
                    break
                if irclib.GLOBAL_BYPASS_PERMISSION in permissions:
                    return [irclib.GLOBAL_BYPASS_PERMISSION]
            if not was_extended:
                break
        return permissions

    def get_permission_state(self, message: irclib.ChannelMessage):
        user = message.user
        group = auto_group(message)

        if user not in self.users:
            self.users[user] = []
        eff: typing.List[str] = self.groups[group].copy()

        eff: typing.List[str] = self._get_permissions_from_parents(eff)
        eff.extend(self.users[user])
        eff: typing.List[str] = self._get_permissions_from_parents(eff)
        # if 'irclib.bypass.permission' in eff:
        #     return ['irclib.bypass.permission']
        if group in ['moderator', 'broadcaster']:
            eff.append(irclib.LOCAL_BYPASS_PERMISSION_TEMPLATE.format(message.channel))
            # eff.append(f'irclib.bypass.permission.local.{message.channel}')
        return eff

    def update(self, dict_: dict):
        for k, v in dict_.items():
            if k.startswith('group.'):
                gn = k.replace('group.', '')
                if gn in self.groups:
                    self.groups[gn].extend(v)
                else:
                    self.groups[gn] = v
            else:
                if k in self.users:
                    self.users[k].extend(v)
                else:
                    self.users[k] = v

    def __iter__(self):
        for i in self.users:
            yield i
        for i in self.groups:
            yield f'group.{i}'

    def __getitem__(self, item):
        if item.startswith('group.'):
            return self.groups[item.replace('group.', '')]
        else:
            return self.users[item]

    def __setitem__(self, key, value):
        if key.startswith('group.'):
            self.groups[key.replace('group.', '')] = value
        else:
            self.users[key] = value

    def fix(self):
        for key in self:
            new = []
            for perm in self[key].copy():
                if perm in new:
                    continue
                new.append(perm)
            self[key] = new
