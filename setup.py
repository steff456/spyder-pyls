#!/usr/bin/env python

# Standard library imports
import ast
import os

# Third party imports
from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))


def get_version():
    """Get version."""
    with open(os.path.join(HERE, 'pyls', '_version.py'), 'r') as f:
        data = f.read()
    lines = data.split('\n')
    for line in lines:
        if line.startswith('VERSION_INFO'):
            version_tuple = ast.literal_eval(line.split('=')[-1].strip())
            version = '.'.join(map(str, version_tuple))
            break
    return version


def get_readme():
    """Load README.md file."""
    with open('README.md', 'r') as fh:
        data = fh.read()
    return data


setup(
    name='spyder-pyls',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=get_version(),

    description='Python Language Server for the Language Server Protocol',

    long_description=get_readme(),
    long_description_content_type='text/markdown',

    # The project's main homepage.
    url='https://github.com/spyder/spyder-pyls',

    author='Palantir Technologies, Inc. and the Spyder development team',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'test', 'test.*']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'configparser; python_version<"3.0"',
        'future>=0.14.0',
        'futures; python_version<"3.2"',
        'backports.functools_lru_cache; python_version<"3.2"',
        'jedi>=0.13.2',
        'python-jsonrpc-server>=0.1.0',
        'pluggy',
        'pycodestyle',
        'pydocstyle>=2.0.0',
        'pyflakes>=1.6.0',
        'rope>=0.10.5'
    ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[test]
    extras_require={
        'all': [
            'autopep8',
            'mccabe',
            'pylint',
            'yapf',
        ],
        'autopep8': ['autopep8'],
        'mccabe': ['mccabe'],
        'pylint': ['pylint'],
        'yapf': ['yapf'],
        'test': ['pylint', 'pytest', 'mock', 'pytest-cov', 'coverage'],
    },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'pyls = pyls.__main__:main',
        ],
        'pyls': [
            'autopep8 = pyls.plugins.autopep8_format',
            'jedi_completion = pyls.plugins.jedi_completion',
            'jedi_definition = pyls.plugins.definition',
            'jedi_hover = pyls.plugins.hover',
            'jedi_highlight = pyls.plugins.highlight',
            'jedi_references = pyls.plugins.references',
            'jedi_signature_help = pyls.plugins.signature',
            'jedi_symbols = pyls.plugins.symbols',
            'mccabe = pyls.plugins.mccabe_lint',
            'preload = pyls.plugins.preload_imports',
            'pycodestyle = pyls.plugins.pycodestyle_lint',
            'pydocstyle = pyls.plugins.pydocstyle_lint',
            'pyflakes = pyls.plugins.pyflakes_lint',
            'pylint = pyls.plugins.pylint_lint',
            'rope_completion = pyls.plugins.rope_completion',
            'rope_rename = pyls.plugins.rope_rename',
            'yapf = pyls.plugins.yapf_format',
        ]
    },
)
