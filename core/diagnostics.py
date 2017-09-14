import os
import sublime
from ..core.url import filename_to_uri, uri_to_filename
from ..core.settings import show_diagnostics_phantoms, diagnostics_highlight_style, auto_show_diagnostics_panel
from ..core.workspace import is_in_workspace, get_project_path
from ..core.panels import ensure_diagnostics_panel
from ..rpc.protocol import Diagnostic, DiagnosticSeverity

UNDERLINE_FLAGS = (sublime.DRAW_SQUIGGLY_UNDERLINE
                   | sublime.DRAW_NO_OUTLINE
                   | sublime.DRAW_NO_FILL
                   | sublime.DRAW_EMPTY_AS_OVERWRITE)

BOX_FLAGS = sublime.DRAW_NO_FILL | sublime.DRAW_EMPTY_AS_OVERWRITE

window_file_diagnostics = dict(
)  # type: Dict[int, Dict[str, Dict[str, List[Diagnostic]]]]

diagnostic_severity_names = {
    DiagnosticSeverity.Error: "error",
    DiagnosticSeverity.Warning: "warning",
    DiagnosticSeverity.Information: "info",
    DiagnosticSeverity.Hint: "hint"
}

diagnostic_severity_scopes = {
    DiagnosticSeverity.Error: 'markup.deleted.lsp sublimelinter.mark.error markup.error.lsp',
    DiagnosticSeverity.Warning: 'markup.changed.lsp sublimelinter.mark.warning markup.warning.lsp',
    DiagnosticSeverity.Information: 'markup.inserted.lsp sublimelinter.gutter-mark markup.info.lsp',
    DiagnosticSeverity.Hint: 'markup.inserted.lsp sublimelinter.gutter-mark markup.info.suggestion.lsp'
}

def format_severity(severity: int) -> str:
    return diagnostic_severity_names.get(severity, "???")


def get_line_diagnostics(view, point):
    row, _ = view.rowcol(point)
    diagnostics = get_diagnostics_for_view(view)
    return tuple(
        diagnostic for diagnostic in diagnostics
        if diagnostic.range.start.row <= row <= diagnostic.range.end.row
    )


def get_diagnostics_for_view(view: sublime.View) -> 'List[Diagnostic]':
    window = view.window()
    file_path = view.file_name()
    origin = 'lsp'
    if window.id() in window_file_diagnostics:
        file_diagnostics = window_file_diagnostics[window.id()]
        if file_path in file_diagnostics:
            if origin in file_diagnostics[file_path]:
                return file_diagnostics[file_path][origin]
    return []


def update_file_diagnostics(window: sublime.Window, file_path: str, source: str,
                            diagnostics: 'List[Diagnostic]'):
    if diagnostics:
        window_file_diagnostics.setdefault(window.id(), dict()).setdefault(
            file_path, dict())[source] = diagnostics
    else:
        if window.id() in window_file_diagnostics:
            file_diagnostics = window_file_diagnostics[window.id()]
            if file_path in file_diagnostics:
                if source in file_diagnostics[file_path]:
                    del file_diagnostics[file_path][source]
                if not file_diagnostics[file_path]:
                    del file_diagnostics[file_path]


phantom_sets_by_buffer = {}  # type: Dict[int, sublime.PhantomSet]


def update_diagnostics_phantoms(view: sublime.View, diagnostics: 'List[Diagnostic]'):
    global phantom_sets_by_buffer

    buffer_id = view.buffer_id()
    if not show_diagnostics_phantoms or view.is_dirty():
        phantoms = None
    else:
        phantoms = list(
            create_phantom(view, diagnostic) for diagnostic in diagnostics)
    if phantoms:
        phantom_set = phantom_sets_by_buffer.get(buffer_id)
        if not phantom_set:
            phantom_set = sublime.PhantomSet(view, "lsp_diagnostics")
            phantom_sets_by_buffer[buffer_id] = phantom_set
        phantom_set.update(phantoms)
    else:
        phantom_sets_by_buffer.pop(buffer_id, None)


def update_diagnostics_regions(view: sublime.View, diagnostics: 'List[Diagnostic]', severity: int):
    region_name = "lsp_" + format_severity(severity)
    if show_diagnostics_phantoms and not view.is_dirty():
        regions = None
    else:
        regions = list(diagnostic.range.to_region(view) for diagnostic in diagnostics
                       if diagnostic.severity == severity)
    if regions:
        scope_name = diagnostic_severity_scopes[severity]
        view.add_regions(
            region_name, regions, scope_name, "dot",
            UNDERLINE_FLAGS if diagnostics_highlight_style == "underline" else BOX_FLAGS)
    else:
        view.erase_regions(region_name)


def update_diagnostics_in_view(view: sublime.View, diagnostics: 'List[Diagnostic]'):
    if view and view.is_valid():
        update_diagnostics_phantoms(view, diagnostics)
        for severity in range(DiagnosticSeverity.Error, DiagnosticSeverity.Information):
            update_diagnostics_regions(view, diagnostics, severity)


def update_diagnostics_panel(window):
    assert window, "missing window!"
    base_dir = get_project_path(window)

    panel = ensure_diagnostics_panel(window)
    assert panel, "must have a panel now!"

    if window.id() in window_file_diagnostics:
        active_panel = window.active_panel()
        is_active_panel = (active_panel == "output.diagnostics")
        panel.settings().set("result_base_dir", base_dir)
        panel.set_read_only(False)
        file_diagnostics = window_file_diagnostics[window.id()]
        if file_diagnostics:
            to_render = []
            for file_path, source_diagnostics in file_diagnostics.items():
                relative_file_path = os.path.relpath(file_path, base_dir) if base_dir else file_path
                if source_diagnostics:
                    to_render.append(format_diagnostics(relative_file_path, source_diagnostics))
            panel.run_command("lsp_update_panel", {"characters": "\n".join(to_render)})
            if auto_show_diagnostics_panel and not active_panel:
                window.run_command("show_panel",
                                   {"panel": "output.diagnostics"})
        else:
            panel.run_command("lsp_clear_panel")
            if auto_show_diagnostics_panel and is_active_panel:
                window.run_command("hide_panel",
                                   {"panel": "output.diagnostics"})
        panel.set_read_only(True)


def format_diagnostic(diagnostic: Diagnostic) -> str:
    location = "{:>8}:{:<4}".format(
        diagnostic.range.start.row + 1, diagnostic.range.start.col + 1)
    message = diagnostic.message.replace("\n", " ").replace("\r", "")
    return " {}\t{:<12}\t{:<10}\t{}".format(
        location, diagnostic.source, format_severity(diagnostic.severity), message)


def format_diagnostics(file_path, origin_diagnostics):
    content = " ◌ {}:\n".format(file_path)
    for origin, diagnostics in origin_diagnostics.items():
        for diagnostic in diagnostics:
            item = format_diagnostic(diagnostic)
            content += item + "\n"
    return content


def remove_diagnostics(view: sublime.View):
    """Removes diagnostics for a file if no views exist for it
    """
    window = sublime.active_window()

    file_path = view.file_name()
    if not window.find_open_file(view.file_name()):
        update_file_diagnostics(window, file_path, 'lsp', [])
        update_diagnostics_panel(window)
    else:
        debug('file still open?')


def handle_diagnostics(update: 'Any'):
    file_path = uri_to_filename(update.get('uri'))
    window = sublime.active_window()

    if not is_in_workspace(window, file_path):
        debug("Skipping diagnostics for file", file_path,
              " it is not in the workspace")
        return

    diagnostics = list(
        Diagnostic.from_lsp(item) for item in update.get('diagnostics', []))

    view = window.find_open_file(file_path)

    # diagnostics = update.get('diagnostics')

    update_diagnostics_in_view(view, diagnostics)

    # update panel if available

    origin = 'lsp'  # TODO: use actual client name to be able to update diagnostics per client

    update_file_diagnostics(window, file_path, origin, diagnostics)
    update_diagnostics_panel(window)
