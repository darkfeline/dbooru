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

"""dbooru.handlers.base

This module contains the base classes for implemention file and inode handling
behavior.

"""

import errno

import llfuse


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


class BaseInodeHandler:

    """Base class that implements the interface for handling operations on inodes.

    """

    # pylint: disable=unused-argument

    def access(self, mode, ctx):
        raise llfuse.FUSEError(errno.ENOSYS)

    def create(self, name, mode, flags, ctx):
        raise llfuse.FUSEError(errno.ENOSYS)

    def getattr(self):
        raise llfuse.FUSEError(errno.ENOSYS)

    def getxattr(self, name):
        raise llfuse.FUSEError(errno.ENOSYS)

    def link(self, new_parent_inode, new_name):
        raise llfuse.FUSEError(errno.ENOSYS)

    def listxattr(self):
        raise llfuse.FUSEError(errno.ENOSYS)

    def lookup(self, name):
        raise llfuse.FUSEError(errno.ENOSYS)

    def mkdir(self, name, mode, ctx):
        raise llfuse.FUSEError(errno.ENOSYS)

    def mknod(self, name, mode, rdev, ctx):
        raise llfuse.FUSEError(errno.ENOSYS)

    def open(self, flags):
        raise llfuse.FUSEError(errno.ENOSYS)

    def opendir(self):
        raise llfuse.FUSEError(errno.ENOSYS)

    def readlink(self):
        raise llfuse.FUSEError(errno.ENOSYS)

    def removexattr(self, name):
        raise llfuse.FUSEError(errno.ENOSYS)

    def rename(self, name_old, inode_parent_new, name_new):
        raise llfuse.FUSEError(errno.ENOSYS)

    def rmdir(self, name):
        raise llfuse.FUSEError(errno.ENOSYS)

    def setattr(self, attr):
        raise llfuse.FUSEError(errno.ENOSYS)

    def setxattr(self, inode, name, value):
        raise llfuse.FUSEError(errno.ENOSYS)

    def symlink(self, name, target, ctx):
        raise llfuse.FUSEError(errno.ENOSYS)

    def unlink(self, name):
        raise llfuse.FUSEError(errno.ENOSYS)
