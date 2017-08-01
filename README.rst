gistfuse
========

``gistfuse`` is a small tool to provide read-only access to users' gists via
a FUSE interface.

installation
------------

::

    git clone https://github.com/ercas/gistfuse && sudo pip3 install gistfuse/

usage
-----

::

    $ gistfuse --help
    Usage: gistfuse [options] mountpoint

    Options:
      -h, --help            show this help message and exit
      -u USERS, --users=USERS
                            A comma-separated list of additional users whose gists
                            should be made available

    $ mkdir gistfuse/ && gistfuse -u eevee,gruber,diracdeltas gistfuse/ &

    $ ls gistfuse
    diracdeltas  eevee  ercas  gruber

    $ cat gistfuse/gruber/Liberal\ Regex\ Pattern\ for\ All\ URLs | head -n 10
    The regex patterns in this gist are intended to match any URLs,
    including "mailto:foo@example.com", "x-whatever://foo", etc. For a
    pattern that attempts only to match web URLs (http, https), see:
    https://gist.github.com/gruber/8891611


    # Single-line version of pattern:

    (?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))

    $ fusermount -u gistfuse/

possible future features
------------------------
* updating and deleting of gists?
* creating of new gists?
* use directories to group multiple files that appear in the same gist?
