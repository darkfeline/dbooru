"""dbooru.fuseop

This module defines FUSE operations.

"""

import errno
import os

import llfuse

from dbooru.backend import DbooruBackend


def _do_os(func, *args, **kwargs):
    """Do low level OS call and handle errors.

    This function wraps any raised OSErrors for the FUSE library.  Call
    anything that could raise an OSError using this!

    """
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
        self.backend = DbooruBackend(root)
        self.fh_count_table = None
        self.fh_handler_table = None
        self.ino_handler_table = None

    def init(self):
        """Set up."""
        self.fh_count_table = {}
        self.fh_handler_table = {}
        self.ino_handler_table = {}

    def destroy(self):
        """Tear down."""

    ###########################################################################
    # General handlers
    def statfs(self):
        return _do_os(os.statvfs, self.root)

    ###########################################################################
    # File handlers
    def write(self, fh, off, buf):
        return self.fh_handler_table[fh].write(off, buf)

    def flush(self, fh):
        """Called on close()

        Does not mean that the fh is finished being used, release() handles
        that.

        """
        self.fh_handler_table[fh].flush()

    def fsync(self, fh, datasync):
        self.fh_handler_table[fh].fsync(datasync)

    def fsyncdir(self, fh, datasync):
        self.fh_handler_table[fh].fsyncdir(datasync)

    def read(self, fh, off, size):
        return self.fh_handler_table[fh].read(off, size)

    def readdir(self, fh, off):
        return self.fh_handler_table[fh].readdir(off)

    def release(self, fh):
        """Finally close fh.

        Possibly called on close().  Called once for each open().

        """
        self._release_with_func(
            fh, self.fh_handler_table[fh].release)

    def releasedir(self, fh):
        self._release_with_func(
            fh, self.fh_handler_table[fh].releasedir)

    def _release_with_func(self, fh, func):
        """Decrement fh count and call function when zero."""
        self.fh_count_table[fh] -= 1
        if self.fh_count_table[fh] < 1:
            func()
            del self.fh_count_table[fh]
            del self.fh_handler_table[fh]

    ###########################################################################
    # General inode handlers
    def forget(self, inode_list):
        raise NotImplementedError

    ###########################################################################
    # Inode handlers
    def access(self, inode, mode, ctx):
        pass

    def create(self, inode_parent, name, mode, flags, ctx):
        pass

    def getattr(self, inode):
        pass

    def getxattr(self, inode, name):
        pass

    def listxattr(self, inode):
        pass

    def lookup(self, parent_inode, name):
        pass

    def mkdir(self, parent_inode, name, mode, ctx):
        pass

    def mknod(self, parent_inode, name, mode, rdev, ctx):
        pass

    def open(self, inode, flags):
        pass

    def opendir(self, inode):
        pass

    def readlink(self, inode):
        pass

    def removexattr(self, inode, name):
        pass

    def rename(self, inode_parent_old, name_old, inode_parent_new, name_new):
        pass

    def rmdir(self, inode_parent, name):
        pass

    def setattr(self, inode, attr):
        pass

    def setxattr(self, inode, name, value):
        pass

    def symlink(self, inode_parent, name, target, ctx):
        pass

    def unlink(self, parent_inode, name):
        pass


class BaseFileHandler:

    """Base class that implements the interface for handling operations on file
    handlers.

    """

    # pylint: disable=unused-argument

    def write(self, off, buf):
        raise llfuse.FUSEError(errno.ENOSYS)

    def flush(self):
        raise llfuse.FUSEError(errno.ENOSYS)

    def fsync(self, datasync):
        raise llfuse.FUSEError(errno.ENOSYS)

    def fsyncdir(self, datasync):
        raise llfuse.FUSEError(errno.ENOSYS)

    def read(self, off, size):
        raise llfuse.FUSEError(errno.ENOSYS)

    def readdir(self, off):
        raise llfuse.FUSEError(errno.ENOSYS)

    def release(self):
        raise llfuse.FUSEError(errno.ENOSYS)

    def releasedir(self):
        raise llfuse.FUSEError(errno.ENOSYS)


class RawFileHandler:

    """File handling for actual files."""

    def __init__(self, fh):
        self.fh = fh

    def write(self, off, buf):
        return _do_os(os.pwrite, self.fh, buf, off)

    def flush(self):
        pass

    def fsync(self, datasync):
        if datasync:
            _do_os(os.fdatasync, self.fh)
        else:
            _do_os(os.fsync, self.fh)

    fsyncdir = fsync

    def read(self, off, size):
        return _do_os(os.pread, self.fh, size, off)

    def readdir(self, off):
        names = _do_os(llfuse.listdir, self.fh)  # pylint: disable=no-member
        while off < len(names):
            name = names[off]
            off += 1
            yield (name.encode(), _do_os(os.stat, name, dir_fd=self.fh), off)

    def release(self):
        _do_os(os.close, self.fh)

    releasedir = release


class BaseInodeHandler:

    """Base class that implements the interface for handling operations on inodes.

    """

    def access(self, mode, ctx):
        raise NotImplementedError

    def create(self, name, mode, flags, ctx):
        raise NotImplementedError

    def getattr(self):
        raise NotImplementedError

    def getxattr(self, name):
        raise NotImplementedError

    def listxattr(self):
        raise NotImplementedError

    def lookup(self, name):
        raise NotImplementedError

    def mkdir(self, name, mode, ctx):
        raise NotImplementedError

    def mknod(self, name, mode, rdev, ctx):
        raise NotImplementedError

    def open(self, flags):
        raise NotImplementedError

    def opendir(self):
        raise NotImplementedError

    def readlink(self):
        raise NotImplementedError

    def removexattr(self, name):
        raise NotImplementedError

    def rename(self, name_old, inode_parent_new, name_new):
        raise NotImplementedError

    def rmdir(self, name):
        raise NotImplementedError

    def setattr(self, attr):
        raise NotImplementedError

    def setxattr(self, inode, name, value):
        raise NotImplementedError

    def symlink(self, name, target, ctx):
        raise NotImplementedError

    def unlink(self, name):
        raise NotImplementedError


class RawInodeHandler:

    def access(self, mode, ctx):
        raise NotImplementedError

    def create(self, name, mode, flags, ctx):
        raise NotImplementedError

    def getattr(self):
        raise NotImplementedError

    def getxattr(self, name):
        raise NotImplementedError

    def listxattr(self):
        raise NotImplementedError

    def lookup(self, name):
        raise NotImplementedError

    def mkdir(self, name, mode, ctx):
        raise NotImplementedError

    def mknod(self, name, mode, rdev, ctx):
        raise NotImplementedError

    def open(self, flags):
        raise NotImplementedError

    def opendir(self):
        raise NotImplementedError

    def readlink(self):
        raise NotImplementedError

    def removexattr(self, name):
        raise NotImplementedError

    def rename(self, name_old, inode_parent_new, name_new):
        raise NotImplementedError

    def rmdir(self, name):
        raise NotImplementedError

    def setattr(self, attr):
        raise NotImplementedError

    def setxattr(self, inode, name, value):
        raise NotImplementedError

    def symlink(self, name, target, ctx):
        raise NotImplementedError

    def unlink(self, name):
        raise NotImplementedError
