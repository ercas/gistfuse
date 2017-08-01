#!/usr/bin/env python2

import errno
import dateutil.parser
import fuse
import itertools
import requests
import stat
import sys
import time

import api

DIR_MODE = stat.S_IFDIR | 0o755
FILE_MODE = stat.S_IFREG | 0o444

def iso_to_unixtime(iso):
    """ Convert an ISO 8601 date string to a Unix time timestamp

    Args:
        iso: The ISO 8601 date string
    """

    return int(dateutil.parser.parse(iso).strftime("%s"))

class File(object):

    def __init__(self, file_json, ctime = None, mtime = None):
        """ Initialize a File object

        Args:
            file_json: A dict of the file. These are the values of items in the
                "files" field of a gist JSON
            ctime: The file's creation time
            mtime: The file's creation time
        """

        self.url = file_json["raw_url"]

        now = time.time()
        self.ctime = ctime or now
        self.mtime = mtime or now
        self.size = file_json["size"]

        # Used for lazy retrieval
        self.content = None

    def getattr(self):
        return {
            "st_mode": FILE_MODE,
            "st_ctime": self.ctime,
            "st_mtime": self.mtime,
            "st_atime": time.time(),
            "st_size": self.size
        }

    def read(self, size, offset):
        # Lazy retrieval of gist content: retrieve and cache for the first
        # read; reuse that cache for future reads
        if (self.content is None):
            response = requests.get(self.url)
            assert (response.status_code == 200)
            self.content = response.content.decode()
        return self.content

class GistUser(object):

    def __init__(self, gists):
        """ Initialize a GistUser object

        Args:
            gists: A dict of the full JSON response to a request for a user's
                gists. See:
                https://developer.github.com/v3/gists/#list-a-users-gists
        """

        # A dictionary where the keys are unique filenames and the values are
        # File objects corresponding to those filenames. In the case of
        # duplicate filenames, "-%d" is appended.
        self.files = {}

        for gist in gists:
            for raw_filename in gist["files"]:

                # Choose a unique filename
                filename = raw_filename
                i = 1
                while (filename in self.files):
                    filename = "%s-%d" % (raw_filename, i)
                    i += 1

                self.files[filename] = File(
                    gist["files"][raw_filename],
                    iso_to_unixtime(gist["created_at"]),
                    iso_to_unixtime(gist["updated_at"])
                )

    def getattr(self):
        now = time.time()
        return {
            "st_mode": DIR_MODE,
            "st_ctime": now,
            "st_mtime": now,
            "st_atime": now,
            "st_nlink": len(self.files),
            "st_size": 1
        }

    def readdir(self):
        return self.files.keys()

class GistFuse(fuse.Operations):

    def __init__(self, additional_users = []):
        self.api = api.GistAPI()

        now = time.time()
        self.root = {
            "st_mode": DIR_MODE,
            "st_ctime": now,
            "st_mtime": now,
            "st_atime": now,
            "st_nlink": 2
        }

        # A dictionary where the keys are usernames and the values are GistUser
        # objects corresponding to those users
        self.users = {}

        for username in ([self.api.auth["username"]] + additional_users):
            try:
                self.users[username] = GistUser(self.api.gists(username))
            except AssertionError:
                print("Invalid user \"%s\"" % username)

    def open(self, path, flags):
        return 0

    def getattr(self, path, fh = None):
        if (path == "/"):
            return self.root
        else:
            return self._find(path).getattr()

    def read(self, path, size, offset, fh):
        return self._find(path).read(size, offset)

    def readdir(self, path, fh):
        if (path == "/"):
            return self.users.keys()
        else:
            return self._find(path).readdir()

    def _find(self, path):
        """ Return a GistUser or File object corresponding to the given path

        Args:
            path: The path to resolve

        Returns:
            A GistUser or File object

        Raises:
            fuse.FuseOSError(errno.ENOENT) if no such user or file exists
        """
        parts = path.split("/")[1:]

        user = parts[0]
        if (len(parts) == 1):
            if (user in self.users):
                return self.users[user]
        elif (len(parts) == 2):
            filename = parts[1]
            files = self.users[user].files
            if (filename in files):
                return files[filename]

        raise fuse.FuseOSError(errno.ENOENT)

if (__name__ == "__main__"):
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-u", "--users", dest = "users", default = "",
                      help = "A comma-separated list of additional users "
                             "whose gists should be made available",
                      metavar = "USERS")
    (options, args) = parser.parse_args()

    if (options.users != ""):
        users = options.users.split(",")
    else:
        users = []

    mountpoint = args[0]
    fuse.FUSE(
        GistFuse(users),
        mountpoint,
        foreground = True
    )
