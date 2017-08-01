#!/usr/bin/env python3

import fuse
import gistfuse

def main():
    import optparse
    parser = optparse.OptionParser(usage = "usage: %prog [options] mountpoint")
    parser.add_option("-u", "--users", dest = "users", default = "",
                      help = "A comma-separated list of additional users "
                             "whose gists should be made available",
                      metavar = "USERS")
    (options, args) = parser.parse_args()

    if (options.users != ""):
        users = options.users.split(",")
    else:
        users = []

    if (len(args) == 1):
        mountpoint = args[0]
        fuse.FUSE(
            gistfuse.GistFuse(users),
            mountpoint,
            foreground = True
        )
    else:
        parser.print_help()

if (__name__ == "__main__"):
    main()
