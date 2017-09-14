import sublime
import sublime_plugin
from ..core.panels import ensure_diagnostics_panel
from ..core.diagnostics import format_severity

class LspShowDiagnosticsPanelCommand(sublime_plugin.WindowCommand):
    def run(self):
        ensure_diagnostics_panel(self.window)
        self.window.run_command("show_panel", {"panel": "output.diagnostics"})


class LspClearPanelCommand(sublime_plugin.TextCommand):
    """
    A clear_panel command to clear the error panel.
    """

    def run(self, edit):
        self.view.erase(edit, sublime.Region(0, self.view.size()))


class LspUpdatePanelCommand(sublime_plugin.TextCommand):
    """
    A update_panel command to update the error panel with new text.
    """

    def run(self, edit, characters):
        self.view.replace(edit, sublime.Region(0, self.view.size()), characters)

        # Move cursor to the end
        selection = self.view.sel()
        selection.clear()
        selection.add(sublime.Region(self.view.size(), self.view.size()))
