# -*- coding: utf-8 -*-
# From: https://github.com/rdegges/skele-cli/blob/master/setup.py

from setuptools import setup, find_packages, Command
from te2_sdk import __version__
from subprocess import call

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()


# Test Runner Command
class RunTests(Command):
    """Run all tests."""
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def run():
        """Run all tests!"""
        errno = call(['pytest', '--cov=te2_sdk', '--cov-report=term-missing'])
        raise SystemExit(errno)


setup(
    name='te2-sdk',
    version=__version__,
    description='Simple Wrapper for Terraform Enterprise 2 Jobs',
    long_description=readme,
    author='Rory Chatterton',
    author_email='rchatterton@westpac.com.au',
    url='https://github.com/westpac-cloud-engineering/Terraform-Enterprise-2-Python-SDK',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=['requests'],
    extras_require={
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    cmdclass={'test': RunTests},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Text Processing"
    ]
)
