"""dbooru.fuseop

This module defines FUSE operations.

"""

import os

import llfuse

from dbooru.resource import Loader

def _do_os(func, *args, **kwargs):
    """Do low level OS call and handle errors."""
    try:
        return func(*args, **kwargs)
    except OSError as err:
        raise llfuse.FUSEError(err.errno)

class FUSEOp(llfuse.Operations):
    """dbooru implementation of FUSE operations."""

    ###########################################################################
    # Set up
    def __init__(self, root):
        """Initialize handler."""
        super().__init__()
        self.root = root
        self.loader = Loader(root)
        self.fh_table = None
        self.ino_table = None

    def init(self):
        """Set up."""
        self.fh_table = {}
        self.ino_table = {}

    def destroy(self):
        """Tear down."""

    ###########################################################################
    # General handlers
    def statfs(self):
        return _do_os(os.statvfs, self.root)

    ###########################################################################
    # File handlers
    def write(self, fh, off, buf):
        return _do_os(os.pwrite, fh, buf, off)

    def flush(self, fh):
        """Called on close()

        Does not mean fh is finished, release() handles that.

        """

    def fsync(self, fh, datasync):
        if datasync:
            _do_os(os.fdatasync, fh)
        else:
            _do_os(os.fsync, fh)

    fsyncdir = fsync

    def read(self, fh, off, size):
        return _do_os(os.pread, fh, size, off)

    def readdir(self, fh, off):
        names = _do_os(llfuse.listdir, fh)
        while off < len(names):
            name = names[off]
            off += 1
            yield (name.encode(), _do_os(os.stat, name, dir_fd=fh), off)

    def release(self, fh):
        """Finally close fh.

        Possibly called on close(). Called once for each open().

        """
        self.fh_table[fh] -= 1
        if self.fh_table[fh] < 1:
            _do_os(os.close, fh)
            del self.fh_table[fh]

    releasedir = release

    ###########################################################################
    # Inode handlers

