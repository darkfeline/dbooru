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

"""dbooru.oslib

This module provides OS helper tools.

"""

import llfuse


def do_os(func, *args, **kwargs):
    """Do low level OS call and handle errors.

    This function wraps any raised OSErrors for the FUSE library.  Call
    anything that could raise an OSError using this!

    """
    try:
        return func(*args, **kwargs)
    except OSError as err:
        raise llfuse.FUSEError(err.errno)
