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


class _HandleGen:

    """File handle generator."""

    _LIMIT = 2

    def __init__(self):
        self._head = self._LIMIT
        self._unused = []

    def __next__(self):
        if self._unused:
            return self._unused.pop()
        else:
            self._head += 1
            return self._head

    def forget(self, fh):
        if fh > self._head or fh <= self._LIMIT:
            raise ValueError('{} not issued.'.format(fh))
        elif fh in self._unused:
            raise ValueError('{} already forgotten.'.format(fh))
        self._unused.append(fh)


class FUSEOp(llfuse.Operations):
    """dbooru implementation of FUSE operations."""

    ###########################################################################
    # Set up
    def __init__(self, root):
        """Initialize handler."""
        super().__init__()
        self._root = root
        self._backend = DbooruBackend(root)
        self._fh_table = None
        self._ino_table = None
        self._fh_gen = None

    def init(self):
        """Set up."""
        self._fh_table = {}
        # ROOT_INODE isn't detected
        # pylint: disable=no-member
        self._ino_table = {
            llfuse.ROOT_INODE: InoTabEntry(RootInodeHandler(self._root), 1),
        }
        self._fh_gen = _HandleGen()

    def destroy(self):
        """Tear down."""

    ###########################################################################
    # General handlers
    def statfs(self):
        return do_os(os.statvfs, self._root)

    ###########################################################################
    # File handlers
    def _get_fh(self, fh):
        """Return handler for given file handle."""
        return self._fh_table[fh].handler

    def write(self, fh, off, buf):
        return self._get_fh(fh).write(off, buf)

    def flush(self, fh):
        """Called on close()

        Does not mean that the fh is finished being used, release() handles
        that.

        """
        self._get_fh(fh).flush()

    def fsync(self, fh, datasync):
        self._get_fh(fh).fsync(datasync)

    def fsyncdir(self, fh, datasync):
        self._get_fh(fh).fsyncdir(datasync)

    def read(self, fh, off, size):
        return self._get_fh(fh).read(off, size)

    def readdir(self, fh, off):
        return self._get_fh(fh).readdir(off)

    def release(self, fh):
        """Finally close fh.

        Possibly called on close().  Called once for each open().

        """
        self._release_with_func(
            fh, self._get_fh(fh).release)

    def releasedir(self, fh):
        self._release_with_func(
            fh, self._get_fh(fh).releasedir)

    def _release_with_func(self, fh, func):
        """Decrement fh count and call function when zero."""
        entry = self._fh_table[fh]
        count = entry.count - 1
        if count < 1:
            func()
            del self._fh_table[fh]
            self._fh_gen.forget(fh)
        else:
            self._fh_table[fh] = entry._replace(count=count)

    ###########################################################################
    # General inode handlers
    def forget(self, inode_list):
        for inode, nlookup in inode_list:
            entry = self._ino_table[inode]
            count = entry.count - nlookup
            if count < 1:
                del self._ino_table[inode]
            else:
                self._ino_table[inode] = entry._replace(count=count)

    ###########################################################################
    # Inode handlers
    def _get_ino(self, inode):
        """Get handler for inode."""
        return self._ino_table[inode].handler

    def _set_ino(self, handler):
        """Set handler in inode table."""
        self._ino_table[handler.attr.st_ino] = handler

    def _set_fh(self, handler):
        """Set handler in file handle table."""
        fh = next(self._fh_gen)
        self._fh_table[fh] = handler
        return fh

    def access(self, inode, mode, ctx):
        return self._get_ino(inode).access(mode, ctx)

    def create(self, inode_parent, name, mode, flags, ctx):
        return self._get_ino(inode_parent).create(
            name, mode, flags, ctx)

    def getattr(self, inode):
        return self._get_ino(inode).getattr()

    def getxattr(self, inode, name):
        return self._get_ino(inode).getxattr(name)

    def link(self, inode, new_parent_inode, new_name):
        return self._get_ino(inode).link(new_parent_inode, new_name)

    def listxattr(self, inode):
        return self._get_ino(inode).listxattr()

    def lookup(self, parent_inode, name):
        handler = self._get_ino(parent_inode).lookup(name)
        self._set_ino(handler)
        return handler.attr

    def mkdir(self, parent_inode, name, mode, ctx):
        return self._get_ino(parent_inode).mkdir(name, mode, ctx)

    def mknod(self, parent_inode, name, mode, rdev, ctx):
        return self._get_ino(parent_inode).mknod(
            name, mode, rdev, ctx)

    def open(self, inode, flags):
        handler = self._get_ino(inode).open(flags)
        fh = self._set_fh(handler)
        return fh

    def opendir(self, inode):
        handler = self._get_ino(inode).opendir()
        fh = self._set_fh(handler)
        return fh

    def readlink(self, inode):
        return self._get_ino(inode).readlink()

    def removexattr(self, inode, name):
        self._get_ino(inode).removexattr(name)

    def rename(self, inode_parent_old, name_old, inode_parent_new, name_new):
        self._get_ino(inode_parent_old).rename(
            name_old, inode_parent_new, name_new)

    def rmdir(self, inode_parent, name):
        self._get_ino(inode_parent).rmdir(name)

    def setattr(self, inode, attr):
        self._get_ino(inode).setattr(attr)

    def setxattr(self, inode, name, value):
        self._get_ino(inode).setxattr(name, value)

    def symlink(self, inode_parent, name, target, ctx):
        return self._get_ino(inode_parent).symlink(name, target, ctx)

    def unlink(self, parent_inode, name):
        return self._get_ino(parent_inode).unlink(name)
