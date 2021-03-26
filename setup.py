#!/usr/scripts/env python
"""
Blackrock Microsystem Data Loader for Python
"""
from distutils.core import setup
from setuptools import find_packages
import re, io

__version__ = re.search(
    r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
    io.open('bmloader/__init__.py', encoding='utf_8_sig').read()
    ).group(1)

__author__ = 'SungHo Lee'
__email__ = 'shlee@unc.edu'
__url__ = ''

setup(name='bmloader',
      version=__version__,
      description='Blackrock Microsystem Data Loader for Python',
      author=__author__,
      author_email=__email__,
      url=__url__,
      license='GNLv3',
      packages=find_packages(),
      install_requires=['shleeh',
                        'requests',
                        'pandas'],
      scripts=[],
      classifiers=[
            'Development Status :: 4 - Beta',
            'Framework :: Jupyter',
            'Intended Audience :: Science/Research',
            'Topic :: Scientific/Engineering',
            'Natural Language :: English',
            'Programming Language :: Python :: 3.7',
      ],
      keywords = ''
     )
