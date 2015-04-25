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
import time

import llfuse

from dbooru.oslib import do_os

from .base import BaseInodeHandler


class RootInodeHandler(BaseInodeHandler):

    def __init__(self, root):
        stat = do_os(os.statvfs, root)
        now = time.time()
        attr = llfuse.EntryAttributes()
        # pylint: disable=no-member
        attr.st_ino = llfuse.ROOT_INODE
        attr.generation = 0  # used if inodes change after restart
        attr.entry_timeout = 300
        attr.attr_timeout = 300
        attr.st_mode
        attr.st_nlink = 1  # Fix for subdirectories?
        attr.st_uid = do_os(os.getpid)
        attr.st_gid = do_os(os.getgid)
        attr.st_size
        attr.st_blksize = stat.f_bsize
        attr.st_blocks = 1
        attr.st_atime = now
        attr.st_ctime = now
        attr.st_mtime = now
        self.attr = attr

    def access(self, mode, ctx):
        # Everyone can access root inode.  Maybe this should be limited to the
        # original user?
        return True

    def getattr(self):
        return self.attr

    def lookup(self, name):
        raise NotImplementedError

    def opendir(self):
        raise NotImplementedError
