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
