#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os
import re


ROOT = os.path.dirname(__file__)
with open(os.path.join(ROOT, 'rrule34', '__init__.py')) as fd:
    __version__ = re.search("__version__ = '([^']+)'", fd.read()).group(1)

setup(
    name="rrule34",
    version=__version__,
    description="Python dateutil rrule tools."
    "Noticeably natural language formatting of recurences.",
    author="Florian Mounier @ Kozea",
    author_email="fmounier@kozea.fr",
    packages=find_packages(),
    platforms="Any",
    provides=['rrule34'],
    install_requires=["python-dateutil", "babel"],
    tests_require=["pytest"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3"])
