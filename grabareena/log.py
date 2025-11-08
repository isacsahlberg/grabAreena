import logging
# from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys  #, shlex, time

LOGFILE = "~/.grabareena/logs/log.txt"
# LOGFILE = "~/.grabareena/logs/log_testing.txt"

def setup_logging(logging_level):
    # Minimal logging: INFO level, prints to the log file
    root = logging.getLogger()
    root.setLevel(logging_level)

    fmt = "%(asctime)s  %(levelname)-5s  %(name)s  %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
    
    # File handler
    p = Path(LOGFILE).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(p, encoding="utf-8")
    fh.setLevel(logging_level)
    fh.setFormatter(formatter)
    root.addHandler(fh)

    # # Console handler -- uncomment this if you want immediate terminal output, e.g. for debugging
    # ch = logging.StreamHandler(stream=sys.stdout)
    # ch.setLevel(logging_level)
    # ch.setFormatter(formatter)
    # # ch.setFormatter(logging.Formatter(fmt="%(message)s"))
    # root.addHandler(ch)

def log_invocation(argv: list[str] | None = None, program_name="grabareena/run_dev.py"):
    # Record the command that the user ran
    args_list = argv if argv is not None else sys.argv[1:]
    cmd = f"[{program_name}]" + (" " + " ".join(args_list) if args_list else "")
    inv = logging.getLogger(f'{program_name}.invocation')
    if inv.isEnabledFor(logging.DEBUG):
        # add separator line to the log file if we are in DEBUG mode
        logging.getLogger("-"*53).debug("")
    inv.info(f"user ran: {cmd}")


# Add this to the main cli.py
"""
import logging
from .log import setup_logging, log_invocation
~ def main(...):

setup_logging()
log_invocation(argv)  # logs usage command

# arguments
...

log = logging.getLogger("grabareena")
log.info(f"resolved date: {str(day)})

"""
