# Copyright (C) 2015  Allen Li
#
# This file is part of dbooru.
#
# dbooru is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# dbooru is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dbooru.  If not, see <http://www.gnu.org/licenses/>.

"""dbooru.handlers.raw

This module contains implementations for handling files and inodes using the
native file system.

"""

import os

import llfuse

from dbooru.oslib import do_os

from .base import BaseFileHandler, BaseInodeHandler


class RawFileHandler(BaseFileHandler):

    """File handling for actual files."""

    def __init__(self, fh):
        self.fh = fh

    def write(self, off, buf):
        return do_os(os.pwrite, self.fh, buf, off)

    def flush(self):
        pass

    def fsync(self, datasync):
        if datasync:
            do_os(os.fdatasync, self.fh)
        else:
            do_os(os.fsync, self.fh)

    fsyncdir = fsync

    def read(self, off, size):
        return do_os(os.pread, self.fh, size, off)

    def readdir(self, off):
        names = do_os(llfuse.listdir, self.fh)  # pylint: disable=no-member
        while off < len(names):
            name = names[off]
            off += 1
            yield (name.encode(), do_os(os.stat, name, dir_fd=self.fh), off)

    def release(self):
        do_os(os.close, self.fh)

    releasedir = release


class RawInodeHandler(BaseInodeHandler):

    # XXX

    def __init__(self, fh):
        self.fh = fh

    def access(self, mode, ctx):
        raise NotImplementedError

    def create(self, name, mode, flags, ctx):
        raise NotImplementedError

    def getattr(self):
        raise NotImplementedError

    def getxattr(self, name):
        raise NotImplementedError

    def link(self, new_parent_inode, new_name):
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
