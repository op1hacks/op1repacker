#!/usr/bin/env python3
import re
from setuptools import setup


version = re.search(
    "^__version__\s*=\s*'([^']*)'",
    open("main.py").read(),
    re.M
    ).group(1)


setup(name="op1repacker",
      version=version,
      description="Tool for unpacking, modding and repacking OP-1 firmware.",
      author="Richard Lewis",
      author_email="richrd.lewis@gmail.com",
      url="https://github.com/op1hacks/op1repacker/",
      packages=["."],
      entry_points={
          "console_scripts": ["op1repacker=main:main"]
      },
      classifiers=[]
      )
