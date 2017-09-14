import os
import sublime


def get_project_path(window: sublime.Window) -> 'Optional[str]':
    """
    Returns the common root of all open folders in the window
    """
    if len(window.folders()):
        folder_paths = window.folders()
        return folder_paths[0]
    else:
        debug("Couldn't determine project directory")
        return None


def get_common_parent(paths: 'List[str]') -> str:
    """
    Get the common parent directory of multiple paths.

    Python 3.5+ includes os.path.commonpath which does this, however Sublime
    currently embeds Python 3.3.
    """
    return os.path.commonprefix([path + '/' for path in paths]).rstrip('/')


def is_in_workspace(window: sublime.Window, file_path: str) -> bool:
    workspace_path = get_project_path(window)
    if workspace_path is None:
        return False

    common_dir = get_common_parent([workspace_path, file_path])
    return workspace_path == common_dir
