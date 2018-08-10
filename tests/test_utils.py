# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from pytest import mark


@mark.parametrize('node,normalized_node', (
    (None, ({'endpoint': 'http://localhost:9984', 'headers': {}},)),
    ('localhost', ({'endpoint': 'http://localhost:9984', 'headers': {}},)),
    ('http://localhost',
     ({'endpoint': 'http://localhost:9984', 'headers': {}},)),
    ('http://localhost:80',
     ({'endpoint': 'http://localhost:80', 'headers': {}},)),
    ('https://node.xyz',
     ({'endpoint': 'https://node.xyz:443', 'headers': {}},)),
    ('https://node.xyz/path',
     ({'endpoint': 'https://node.xyz:443/path', 'headers': {}},)),
))
def test_single_node_normalization(node, normalized_node):
    from bigchaindb_driver.utils import normalize_nodes, normalize_url
    assert normalize_nodes(normalize_url(node)) == normalized_node


@mark.parametrize('nodes,normalized_nodes', (
    ((), ({'endpoint': 'http://localhost:9984', 'headers': {}},)),
    ([], ({'endpoint': 'http://localhost:9984', 'headers': {}},)),
    (('localhost',
      'https://node.xyz'),
     ({'endpoint': 'http://localhost:9984',
       'headers': {}},
      {'endpoint': 'https://node.xyz:443',
       'headers': {}})),
))
def test_iterable_of_nodes_normalization(nodes, normalized_nodes):
    from bigchaindb_driver.utils import normalize_nodes
    assert normalize_nodes(*nodes) == normalized_nodes
