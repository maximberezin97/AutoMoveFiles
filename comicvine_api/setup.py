from setuptools import setup
setup(
name = 'comicvine_api',
url = 'http://github.com/swc/comicvine_api',
version='1.04',

author='swc/Steve',
author_email='iam@attractive.com',
description='Interface to the comicvine.com API',
license='GPLv2',

long_description="""\
An easy to use API interface to www.comicvine.com
Modified from http://github.com/dbr/tvdb_api

Basic usage is:

>>> import comicvine_api
>>> c = comicvine_api.Comicvine()
>>> iss = c['Y: The Last Man'][1]
>>> iss
<Issue 1 - Unmanned>
>>> iss['issuename']
u'Unmanned'
""",

py_modules = ['comicvine_api', 'comicvine_ui', 'comicvine_exceptions', 'cache'],

classifiers=[
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Multimedia",
    "Topic :: Utilities",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
)
