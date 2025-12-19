from pathlib import Path
import logging
import sys

LOGFILE = "~/.grabareena/logs/log.txt"
# LOGFILE="~/.grabareena/logs/log_testing.txt"
LOGFILE_DEBUG = "~/.grabareena/logs/debug.txt"


def setup_logging(verbose=False):
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    fmt = "%(asctime)s  %(levelname)-5s  %(name)s  %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
    
    # File handler for INFO level (always on)
    p1 = Path(LOGFILE).expanduser()
    p1.parent.mkdir(parents=True, exist_ok=True)
    fh1 = logging.FileHandler(p1, encoding="utf-8")
    fh1.setLevel(logging.INFO)
    fh1.setFormatter(formatter)
    root.addHandler(fh1)

    # File handler for DEBUG level (always on)
    p2 = Path(LOGFILE_DEBUG).expanduser()
    p2.parent.mkdir(parents=True, exist_ok=True)
    fh2 = logging.FileHandler(p2, encoding="utf-8")
    fh2.setLevel(logging.DEBUG)
    fh2.setFormatter(formatter)
    root.addHandler(fh2)

    # Console handler, controlled by --verbose flag
    if verbose:
        ch = logging.StreamHandler(stream=sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)  # ch.setFormatter(logging.Formatter(fmt="%(message)s"))
        root.addHandler(ch)


def log_invocation(argv: list[str] | None = None, program_name="grabareena/run_dev.py"):
    # Record the command that the user ran
    args_list = argv if argv is not None else sys.argv[1:]
    cmd = f"[{program_name}]" + (" " + " ".join(args_list) if args_list else "")
    inv = logging.getLogger(f'{program_name}.invocation')
    if inv.isEnabledFor(logging.DEBUG):
        # add separator line to the log file if we are in DEBUG mode
        logging.getLogger("-"*53).debug("")
    inv.info(f"user ran: {cmd}")
