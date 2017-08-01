#!/usr/bin/env python3

import setuptools

setuptools.setup(
    name = "gistfuse",
    version = "1.0.0",
    description = "A FUSE interface for GitHub Gists",
    packages = ["gistfuse"],
    install_requires = ["fusepy", "requests"],
    entry_points = {"console_scripts": ["gistfuse = gistfuse.__main__:main"]}
)
