import os
import tempfile

from core.config import defaultEditor

def prompt(default=None):
    editor = os.environ.get('EDITOR', defaultEditor) #  try assigning default editor, if fails, use default
    with tempfile.NamedTemporaryFile(mode='r+') as tmpfile: #  create a temporary file and open it
        if default: #  if prompt should have some predefined text
            tmpfile.write(default)
            tmpfile.flush()
        child_pid = os.fork()
        is_child = child_pid == 0

        if is_child:
            os.execvp(editor, [editor, tmpfile.name]) #  opens the file in the editor
        else:
            os.waitpid(child_pid, 0) #  wait till the editor gets closed
            tmpfile.seek(0)
            return tmpfile.read().strip() #  read the file
