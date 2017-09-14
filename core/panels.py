import sublime
from ..core.workspace import get_project_path
from ..rpc.protocol import Diagnostic

PLUGIN_NAME = 'LSP'
OUTPUT_PANEL_SETTINGS = {
    "auto_indent": False,
    "draw_indent_guides": False,
    "draw_white_space": "None",
    "gutter": False,
    'is_widget': True,
    "line_numbers": False,
    "margin": 3,
    "match_brackets": False,
    "scroll_past_end": False,
    "tab_size": 4,
    "translate_tabs_to_spaces": False,
    "word_wrap": False
}


def create_output_panel(window: sublime.Window, name: str) -> sublime.View:
    panel = window.create_output_panel(name)
    settings = panel.settings()
    for key, value in OUTPUT_PANEL_SETTINGS.items():
        settings.set(key, value)
    return panel


def create_references_panel(window: sublime.Window):
    panel = create_output_panel(window, "references")
    panel.settings().set("result_file_regex",
                         r"^\s+\S\s+(\S.+)\s+(\d+):?(\d+)$")
    panel.assign_syntax("Packages/" + PLUGIN_NAME +
                        "/Syntaxes/References.sublime-syntax")
    return panel


def ensure_references_panel(window: sublime.Window):
    return window.find_output_panel("references") or create_references_panel(window)


def create_diagnostics_panel(window):
    panel = create_output_panel(window, "diagnostics")
    panel.settings().set("result_file_regex", r"^\s*\S\s+(\S.*):$")
    panel.settings().set("result_line_regex", r"^\s+([0-9]+):?([0-9]+).*$")
    panel.assign_syntax("Packages/" + PLUGIN_NAME +
                        "/Syntaxes/Diagnostics.sublime-syntax")
    return panel


def ensure_diagnostics_panel(window):
    return window.find_output_panel("diagnostics") or create_diagnostics_panel(window)

