# -*- coding: utf-8 -*-
# From: https://github.com/rdegges/skele-cli/blob/master/setup.py

from setuptools import setup, find_packages, Command
from tfe2_pipeline_helpers import __version__
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

    def run(self):
        """Run all tests!"""
        errno = call(['pytest', '--cov=tfe2_pipeline_helpers', '--cov-report=term-missing'])
        raise SystemExit(errno)


setup(
    name='tfe2_pipeline_helpers',
    version=__version__,
    description='Simple scripts to call TFE2 from Release Pipelines, pulling ancillary information from Consul',
    long_description=readme,
    author='Rory Chatterton',
    author_email='rchatterton@westpac.com.au',
    url='https://github.com/westpac/tfe2_pipeline_helpers',
    license=license,
    packages=find_packages(exclude=('tests', 'docs', 'examples', 'schema')),
    install_requires=['pyhcl', 'jinja2', 'requests'],
    extras_require={
        'test': ['coverage', 'pytest', 'pytest-cov', 'coverage'],
    },
    entry_points={
        'console_scripts': [
            'gpcook=gpcook.main:main',
        ],
    },
    cmdclass={'test': RunTests},
)