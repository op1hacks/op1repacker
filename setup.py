#!/usr/bin/env python3
import re
from setuptools import setup


version = re.search(
    "^__version__\s*=\s*'([^']*)'",
    open("op1repacker/main.py").read(),
    re.M
    ).group(1)

files = [
    "assets/display/*.svg",
    "assets/display/*.json",
    "assets/presets/*/*.aif",
]

setup(name="op1repacker",
      version=version,
      description="Tool for unpacking, modding and repacking OP-1 firmware.",
      author="Richard Lewis",
      author_email="richrd.lewis@gmail.com",
      url="https://github.com/op1hacks/op1repacker/",
      packages=["op1repacker"],
      package_data={"": files},
      install_requires=[
          "svg.path",
      ],
      entry_points={
          "console_scripts": ["op1repacker=op1repacker.main:main"]
      },
      classifiers=[]
      )
