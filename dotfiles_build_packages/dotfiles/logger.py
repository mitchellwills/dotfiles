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
    def __init__(self, message, **kwargs):
        self.message = message
        log(message, **kwargs)

    def __enter__(self):
        _log_frames.append(self)

    def __exit__(self, type, value, traceback):
        _log_frames.pop()

_log_frames = []

class TryLog:
    def __init__(self, message, kwargs):
        self.message = message
        self.kwargs = kwargs

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        if traceback is None:
            success(self.message, **self.kwargs)
        else:
            failed(str(value)+': '+self.message, **self.kwargs)


print_verbose = False
def init(should_print_verbose):
    global print_verbose
    print_verbose = should_print_verbose


def trylog(message, **kwargs):
    return TryLog(message, kwargs)

def log(message, t = NORMAL, verbose = False):
    if not verbose or print_verbose:
        print ('\t'*len(_log_frames)) + t.color + str(message) + bash_normal

def success(message, **kwargs):
    kwargs['t'] = SUCCESS
    log(message, **kwargs)

def failed(message, **kwargs):
    kwargs['t'] = FAILED
    log(message, **kwargs)

def warning(message, **kwargs):
    kwargs['t'] = WARNING
    log(message, **kwargs)

def frame(message, **kwargs):
    return LogFrame(message, **kwargs)

def log_stdout(stdout, stderr):
    for line in stdout.splitlines():
        log(line)
def log_stderr(stdout, stderr):
    for line in stderr.splitlines():
        log(line)

def call(*args, **kwargs):
    log_message = 'runnning: '+str(args[0])
    if 'cwd' in kwargs:
        log_message += '\t(wd='+kwargs['cwd']+')'
    with frame(log_message):
        with trylog('done'):
            if not print_verbose:
                if 'stdout' not in kwargs:
                    kwargs['stdout'] = subprocess.PIPE
                if 'stderr' not in kwargs:
                    kwargs['stderr'] = subprocess.PIPE
            output_handler = kwargs.pop('output_handler', lambda out, err: None)
            p = subprocess.Popen(*args, **kwargs)
            stdout, stderr = p.communicate()
            output_handler(stdout, stderr)
            if p.returncode != 0:
                print stdout
                print stderr
                raise Exception('Error Code: '+str(p.returncode))
