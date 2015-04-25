"""dbooru.fuseop

This module defines the FUSE operations used by dbooru.

"""

from collections import namedtuple
import os

import llfuse

from dbooru.oslib import do_os
from dbooru.backend import DbooruBackend
from dbooru.handlers.root import RootInodeHandler

FileTabEntry = namedtuple('FileTabEntry', ['handler', 'count'])
InoTabEntry = namedtuple('InoTabEntry', ['handler', 'count'])


class FUSEOp(llfuse.Operations):
    """dbooru implementation of FUSE operations."""

    ###########################################################################
    # Set up
    def __init__(self, root):
        """Initialize handler."""
        super().__init__()
        self.root = root
        self.backend = DbooruBackend(root)
        self.fh_table = None
        self.ino_table = None

    def init(self):
        """Set up."""
        self.fh_table = {}
        # ROOT_INODE isn't detected
        # pylint: disable=no-member
        self.ino_table = {
            llfuse.ROOT_INODE: InoTabEntry(RootInodeHandler(), 1),
        }

    def destroy(self):
        """Tear down."""

    ###########################################################################
    # General handlers
    def statfs(self):
        return do_os(os.statvfs, self.root)

    ###########################################################################
    # File handlers
    def _get_fh_handler(self, fh):
        return self.fh_table[fh].handler

    def write(self, fh, off, buf):
        return self._get_fh_handler(fh).write(off, buf)

    def flush(self, fh):
        """Called on close()

        Does not mean that the fh is finished being used, release() handles
        that.

        """
        self._get_fh_handler(fh).flush()

    def fsync(self, fh, datasync):
        self._get_fh_handler(fh).fsync(datasync)

    def fsyncdir(self, fh, datasync):
        self._get_fh_handler(fh).fsyncdir(datasync)

    def read(self, fh, off, size):
        return self._get_fh_handler(fh).read(off, size)

    def readdir(self, fh, off):
        return self._get_fh_handler(fh).readdir(off)

    def release(self, fh):
        """Finally close fh.

        Possibly called on close().  Called once for each open().

        """
        self._release_with_func(
            fh, self._get_fh_handler(fh).release)

    def releasedir(self, fh):
        self._release_with_func(
            fh, self._get_fh_handler(fh).releasedir)

    def _release_with_func(self, fh, func):
        """Decrement fh count and call function when zero."""
        entry = self.fh_table[fh]
        count = entry.count - 1
        if count < 1:
            func()
            del self.fh_table[fh]
        else:
            self.fh_table[fh] = entry._replace(count=count)

    ###########################################################################
    # General inode handlers
    def forget(self, inode_list):
        for inode, nlookup in inode_list:
            entry = self.ino_table[inode]
            count = entry.count - nlookup
            if count < 1:
                del self.ino_table[inode]
            else:
                self.ino_table[inode] = entry._replace(count=count)

    ###########################################################################
    # Inode handlers
    def _get_ino_handler(self, inode):
        return self.ino_table[inode].handler

    def access(self, inode, mode, ctx):
        return self._get_ino_handler(inode).access(mode, ctx)

    def create(self, inode_parent, name, mode, flags, ctx):
        return self._get_ino_handler(inode_parent).create(
            name, mode, flags, ctx)

    def getattr(self, inode):
        return self._get_ino_handler(inode).getattr()

    def getxattr(self, inode, name):
        return self._get_ino_handler(inode).getxattr(name)

    def link(self, inode, new_parent_inode, new_name):
        return self._get_ino_handler(inode).link(new_parent_inode, new_name)

    def listxattr(self, inode):
        return self._get_ino_handler(inode).listxattr()

    def lookup(self, parent_inode, name):
        return self._get_ino_handler(parent_inode).lookup(name)

    def mkdir(self, parent_inode, name, mode, ctx):
        return self._get_ino_handler(parent_inode).mkdir(name, mode, ctx)

    def mknod(self, parent_inode, name, mode, rdev, ctx):
        return self._get_ino_handler(parent_inode).mknod(
            name, mode, rdev, ctx)

    def open(self, inode, flags):
        return self._get_ino_handler(inode).open(flags)

    def opendir(self, inode):
        return self._get_ino_handler(inode).opendir()

    def readlink(self, inode):
        return self._get_ino_handler(inode).readlink()

    def removexattr(self, inode, name):
        self._get_ino_handler(inode).removexattr(name)

    def rename(self, inode_parent_old, name_old, inode_parent_new, name_new):
        self._get_ino_handler(inode_parent_old).rename(
            name_old, inode_parent_new, name_new)

    def rmdir(self, inode_parent, name):
        self._get_ino_handler(inode_parent).rmdir(name)

    def setattr(self, inode, attr):
        self._get_ino_handler(inode).setattr(attr)

    def setxattr(self, inode, name, value):
        self._get_ino_handler(inode).setxattr(name, value)

    def symlink(self, inode_parent, name, target, ctx):
        return self._get_ino_handler(inode_parent).symlink(name, target, ctx)

    def unlink(self, parent_inode, name):
        return self._get_ino_handler(parent_inode).unlink(name)
