import os
import tempfile

from core.config import defaultEditor


def prompt(default=None):
    # try assigning default editor, if fails, use default
    editor = os.environ.get('EDITOR', defaultEditor)
    # create a temporary file and open it
    with tempfile.NamedTemporaryFile(mode='r+') as tmpfile:
        if default:  # if prompt should have some predefined text
            tmpfile.write(default)
            tmpfile.flush()
        child_pid = os.fork()
        is_child = child_pid == 0

        if is_child:
            # opens the file in the editor
            os.execvp(editor, [editor, tmpfile.name])
        else:
            os.waitpid(child_pid, 0)  # wait till the editor gets closed
            tmpfile.seek(0)
            return tmpfile.read().strip()  # read the file
