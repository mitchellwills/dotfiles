import subprocess

bash_normal = '\033[0m'
bash_red = '\033[0;31m'
bash_green = '\033[0;32m'
bash_yellow = '\033[0;33m'

class LogType:
    def __init__(self, color):
        self.color = color

SUCCESS = LogType(bash_green)
FAILED = LogType(bash_red)
WARNING = LogType(bash_yellow)
NORMAL = LogType(bash_normal)

class LogFrame:
    def __init__(self, message, t):
        self.message = message
        log(message, t)

    def __enter__(self):
        _log_frames.append(self)

    def __exit__(self, type, value, traceback):
        _log_frames.pop()

_log_frames = []

class TryLog:
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        if traceback is None:
            success(self.message)
        else:
            failed(str(value)+': '+self.message)

def trylog(message):
    return TryLog(message)

def log(message, t = NORMAL):
    print ('\t'*len(_log_frames)) + t.color + str(message) + bash_normal

def success(message):
    log(message, SUCCESS)

def failed(message):
    log(message, FAILED)

def warning(message):
    log(message, WARNING)

def frame(message, t = NORMAL):
    return LogFrame(message, t)


def call(*args, **kwargs):
    with trylog('runnning: '+str(args[0])):
        if 'stdout' not in kwargs:
            kwargs['stdout'] = subprocess.PIPE
        p = subprocess.Popen(*args, **kwargs)
        stdout, stderr = p.communicate()
        print 'done'
