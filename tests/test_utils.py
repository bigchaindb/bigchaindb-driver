from pytest import mark


@mark.parametrize('node,normalized_node', (
    (None, ('http://localhost:9984',)),
    ('localhost', ('http://localhost:9984',)),
    ('http://localhost', ('http://localhost:9984',)),
    ('http://localhost:80', ('http://localhost:80',)),
    ('https://node.xyz', ('https://node.xyz:443',)),
    ('https://node.xyz/path', ('https://node.xyz:443/path',)),
))
def test_single_node_normalization(node, normalized_node):
    from bigchaindb_driver.utils import _normalize_nodes
    assert _normalize_nodes(node) == normalized_node


@mark.parametrize('nodes,normalized_nodes', (
    ((), ('http://localhost:9984',)),
    ([], ('http://localhost:9984',)),
    (('localhost', 'https://node.xyz'),
     ('http://localhost:9984', 'https://node.xyz:443')),
))
def test_iterable_of_nodes_normalization(nodes, normalized_nodes):
    from bigchaindb_driver.utils import _normalize_nodes
    assert _normalize_nodes(*nodes) == normalized_nodes
