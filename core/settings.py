import sublime

show_status_messages = True
show_view_status = True
auto_show_diagnostics_panel = True
show_diagnostics_phantoms = False
show_diagnostics_in_view_status = True
only_show_lsp_completions = False
diagnostics_highlight_style = "underline"
complete_all_chars = False
log_debug = True
log_server = True
log_stderr = False
# global_client_configs = []  # type: List[ClientConfig]


class Settings(object):

    def __init__(self):
        global_client_configs = []  # type: List[ClientConfig]


settings = Settings()


class ClientConfig(object):
    def __init__(self, name, binary_args, scopes, syntaxes, languageId,
                 enabled=True, init_options=dict(), settings=dict()):
        self.name = name
        self.binary_args = binary_args
        self.scopes = scopes
        self.syntaxes = syntaxes
        self.languageId = languageId
        self.enabled = enabled
        self.init_options = init_options
        self.settings = settings


def read_client_config(name, client_config):
    return ClientConfig(
        name,
        client_config.get("command", []),
        client_config.get("scopes", []),
        client_config.get("syntaxes", []),
        client_config.get("languageId", ""),
        client_config.get("enabled", True),
        client_config.get("initializationOptions", dict())
    )


def load_settings():
    settings_obj = sublime.load_settings("LSP.sublime-settings")
    update_settings(settings_obj)
    settings_obj.add_on_change("_on_new_settings", lambda: update_settings(settings_obj))


def read_bool_setting(settings_obj: sublime.Settings, key: str, default: bool) -> bool:
    val = settings_obj.get(key)
    if isinstance(val, bool):
        return val
    else:
        return default


def read_str_setting(settings_obj: sublime.Settings, key: str, default: str) -> str:
    val = settings_obj.get(key)
    if isinstance(val, str):
        return val
    else:
        return default


def update_settings(settings_obj: sublime.Settings):
    global show_status_messages
    global show_view_status
    global auto_show_diagnostics_panel
    global show_diagnostics_phantoms
    global show_diagnostics_in_view_status
    global only_show_lsp_completions
    global diagnostics_highlight_style
    global complete_all_chars
    global log_debug
    global log_server
    global log_stderr
    # global global_client_configs

    settings.global_client_configs = []
    client_configs = settings_obj.get("clients", {})
    if isinstance(client_configs, dict):
        for client_name, client_config in client_configs.items():
            config = read_client_config(client_name, client_config)
            if config:
                # debug("Config added:", client_name, '(enabled)' if config.enabled else '(disabled)')
                settings.global_client_configs.append(config)
    else:
        raise ValueError("client_configs")

    show_status_messages = read_bool_setting(settings_obj, "show_status_messages", True)
    show_view_status = read_bool_setting(settings_obj, "show_view_status", True)
    auto_show_diagnostics_panel = read_bool_setting(settings_obj, "auto_show_diagnostics_panel", True)
    show_diagnostics_phantoms = read_bool_setting(settings_obj, "show_diagnostics_phantoms", False)
    show_diagnostics_in_view_status = read_bool_setting(settings_obj, "show_diagnostics_in_view_status", True)
    diagnostics_highlight_style = read_str_setting(settings_obj, "diagnostics_highlight_style", "underline")
    only_show_lsp_completions = read_bool_setting(settings_obj, "only_show_lsp_completions", False)
    complete_all_chars = read_bool_setting(settings_obj, "complete_all_chars", True)
    log_debug = read_bool_setting(settings_obj, "log_debug", False)
    log_server = read_bool_setting(settings_obj, "log_server", True)
    log_stderr = read_bool_setting(settings_obj, "log_stderr", False)

