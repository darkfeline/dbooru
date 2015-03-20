"""dbooru.resource

This module contains a class for easy resource location.

"""

import os
import re

class Loader:

    """Load resources."""

    _fid_pattern = re.compile(r'([0-9a-f]{32})(\+\d+)$')

    def __init__(self, root):
        """Initialize loader with root path."""
        self.root = root

    def get_db(self):
        """Get database resource path."""
        return os.path.join(self.root, 'dbooru.db')

    def get_file(self, fid):
        """Get file resource path by file id.

        ID format: <md5sum hex string lowercase>[+<optional index>]

        If index is omitted, it is equivalent to an index of 0.

        Raises:
            InvalidFIDError: Invalid fid.

        """
        match = self._fid_pattern.match(fid)
        if not match:
            raise InvalidFIDError(fid)
        md5sum = match.group(1)
        index = match.group(2)
        # If no index was matched, set to zero.
        # Else, process index match.
        if index is None:
            index = 0
        else:
            # Slice off + and normalize as int.
            index = int(index[1:])
        return os.path.join(self.root, md5sum[:1],
                            '{}+{}'.format(md5sum[1:], index))
        

class InvalidFIDError(Exception):
    """Invalid FID."""

    def __init__(self, fid):
        self.fid = fid
        
    def __str__(self):
        return "Invalid FID: {}".format(self.fid)
