import argparse
import typing


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *a, message_handler=lambda *a: None, **kw):
        super().__init__(*a, **kw)
        self.message_handler = message_handler

    def parse_args(self, args: typing.Optional[typing.Sequence[str]] = None,
                   namespace: typing.Optional[argparse.Namespace] = None) -> typing.Optional[argparse.Namespace]:
        try:
            return super().parse_args(args, namespace)
        except SystemExit:
            return

    def _print_message(self, message: str, file: typing.Optional[typing.IO[str]] = None) -> None:
        self.message_handler(message.rstrip('\n'))
