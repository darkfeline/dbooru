"""dbooru.resource

This module contains a class for easy resource location.

"""

import hashlib
import os
import sqlite3
import tempfile


class DbooruBackend:

    """Backend responsible for all interaction with files and metadata."""

    def __init__(self, root):
        self.root = root

    @property
    def files_dir(self):
        return os.path.join(self.root, 'files')

    @property
    def db_file(self):
        return os.path.join(self.root, 'dbooru.db')

    def create(self):
        """Create a file."""
        return _FileWrapper(self)

    def stat(self, fid):
        """Return a stored file's stat structure."""
        return os.stat(os.path.join(self.files_dir, fid))

    def delete(self, fid):
        """Delete stored file."""
        os.unlink(os.path.join(self.files_dir, fid))
        conn = self.connect_to_db()
        cur = conn.cursor()
        cur.execute('DELETE FROM files WHERE fid=?', fid)
        conn.commit()
        conn.close()

    def connect_to_db(self):
        """Connect to metadata database."""
        return sqlite3.connect(self.db_file)


class _FileWrapper:

    """Wrapper to support file creation in dbooru.

    When an instance is created, a temporary file descriptor is made, which can
    be accessed using the fd attribute.  This file descriptor can be used to
    write the content of the file.  When the file is completely written, it is
    finalized by calling the close() method, which will close the file
    descriptor, calculate its hash to use as its fid, then move the temporary
    file to its final location.

    This class can be used as a context manager, in which case it returns a
    binary writable file object:

        with _FileWrapper(root) as file:
            file.write(b'This is some data.')

    """

    _PROCESS_LENGTH = 10 * (2 ** 20)  # 10 MiB

    def __init__(self, root):
        self._root = root
        self.fd, self._path = tempfile.mkstemp()
        self._file = None

    def __enter__(self):
        self._file = os.fdopen(self.fd, 'wb')
        return self._file

    def __exit__(self, exc_type, exc_value, traceback):
        self._file.close()
        self.close()

    def close(self):
        # Close file descriptor.
        os.close(self.fd)
        # Find hash value and move file to storage.
        hasher = hashlib.sha256()
        with open(self._path, 'rb') as file:
            while True:
                data = file.read(self._PROCESS_LENGTH)
                if not data:
                    break
                hasher.update(data)
        fid = hasher.hexdigest()
        os.rename(self._path, os.path.join(self._root.files_dir, fid))
        # Write necessary metadata for new file.
        conn = self._root.connect_to_db()
        cur = conn.cursor()
        cur.execute('INSERT INTO files VALUES (?)', fid)
        conn.commit()
        conn.close()