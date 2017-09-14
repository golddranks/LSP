from ..core.settings import log_debug

PLUGIN_NAME = 'LSP'


def debug(*args):
    """Print args to the console if the "debug" setting is True."""
    if log_debug:
        printf(*args)


def server_log(binary, *args):
    printf(*args, prefix=binary)


def printf(*args, prefix=PLUGIN_NAME):
    """Print args to the console, prefixed by the plugin name."""
    print(prefix + ":", *args)
