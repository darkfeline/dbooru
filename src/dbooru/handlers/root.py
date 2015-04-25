"""dbooru.handlers.raw

This module contains implementations for handling files and inodes using the
native file system.

"""

import os

import llfuse

from dbooru.oslib import do_os

from .base import BaseInodeHandler


class RootInodeHandler(BaseInodeHandler):

    # XXX

    def access(self, mode, ctx):
        # Everyone can access root inode.  Maybe this should be limited to the
        # original user?
        return True

    def getattr(self):
        attr = llfuse.EntryAttributes()
        # pylint: disable=no-member
        attr.st_ino = llfuse.ROOT_INODE
        attr.generation = 0  # used if inodes change after restart
        attr.entry_timeout = 300
        attr.attr_timeout = 300
        attr.st_mode
        attr.st_nlink
        attr.st_uid
        attr.st_gid
        attr.st_rdev
        attr.st_size
        attr.st_blksize = 4096
        attr.st_blocks = 1
        attr.st_atime
        attr.st_ctime
        attr.st_mtime
        return attr

    def lookup(self, name):
        raise NotImplementedError

    def mkdir(self, name, mode, ctx):
        raise NotImplementedError

    def mknod(self, name, mode, rdev, ctx):
        raise NotImplementedError

    def opendir(self):
        raise NotImplementedError
