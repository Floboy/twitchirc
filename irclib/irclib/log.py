import datetime


def log(level: str, *message: str, sep: str = ' '):
    print('[{}] [{}] {}'.format(datetime.datetime.now().strftime('%H:%M:%S'), level, sep.join(message)))


def info(*message: str):
    log('info', *message)


def warn(*message: str):
    log('warn', *message)
