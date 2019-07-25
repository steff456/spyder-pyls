# Copyright 2017 Palantir Technologies, Inc.
from test.test_utils import version_str2tuple as str2tuple
import jedi
import pytest

from pyls import uris
from pyls.plugins.definition import pyls_definitions
from pyls.workspace import Document


DOC_URI = uris.from_fs_path(__file__)
DOC = """def a():
    pass

print a()


class Directory(object):
    def __init__(self):
        self.members = dict()

    def add_member(self, id, name):
        self.members[id] = name
"""


def test_definitions(config):
    # Over 'a' in print a
    cursor_pos = {'line': 3, 'character': 6}

    # The definition of 'a'
    def_range = {
        'start': {'line': 0, 'character': 4},
        'end': {'line': 0, 'character': 5}
    }

    doc = Document(DOC_URI, DOC)
    assert [{'uri': DOC_URI, 'range': def_range}] == pyls_definitions(config, doc, cursor_pos)


@pytest.mark.skipif(str2tuple(jedi.__version__) <= str2tuple('14.0'),
                    reason='This test fails with previous versions of jedi')
def test_builtin_definition(config):
    # Over 'i' in dict
    cursor_pos = {'line': 8, 'character': 24}

    # No go-to def for builtins
    doc = Document(DOC_URI, DOC)
    assert len(pyls_definitions(config, doc, cursor_pos)) == 1


def test_assignment(config):
    # Over 's' in self.members[id]
    cursor_pos = {'line': 11, 'character': 19}

    # The assignment of 'self.members'
    def_range = {
        'start': {'line': 8, 'character': 13},
        'end': {'line': 8, 'character': 20}
    }

    doc = Document(DOC_URI, DOC)
    assert [{'uri': DOC_URI, 'range': def_range}] == pyls_definitions(config, doc, cursor_pos)
