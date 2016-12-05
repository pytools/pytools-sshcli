# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pytools-sshcli',

    version='0.0.0',

    description='A helper module wrapped around common CLI commands.',
    long_description=long_description,

    url='https://github.com/pytools/pytools-sshcli',

    author='Richard King',
    author_email='richrdkng@gmail.com',

    license='MIT',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='ssh sftp cli command line interface pytools development',

    packages=find_packages(exclude=('docs', 'tests')),

    install_requires=[
        'pytools-cli',
    ],
)
