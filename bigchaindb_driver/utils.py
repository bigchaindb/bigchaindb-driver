"""Set of utilities to support various functionalities of the driver.

Attributes:
    ops_map (dict): Mapping between operation strings and classes.
        E.g.: The string ``'CREATE'`` is mapped to
        :class:`~.CreateOperation`.
"""
from urllib.parse import urlparse, urlunparse


DEFAULT_NODE = 'http://localhost:9984'


class CreateOperation:
    """Class representing the ``'CREATE'`` transaction operation."""


class TransferOperation:
    """Class representing the ``'TRANSFER'`` transaction operation."""


ops_map = {
    'CREATE': CreateOperation,
    'TRANSFER': TransferOperation,
}


def _normalize_operation(operation):
    """Normalizes the given operation string. For now, this simply means
    converting the given string to uppercase, looking it up in
    :attr:`~.ops_map`, and returning the corresponding class if
    present.

    Args:
        operation (str): The operation string to convert.

    Returns:
        The class corresponding to the given string,
        :class:`~.CreateOperation` or :class:`~TransferOperation`.

        .. important:: If the :meth:`str.upper` step, or the
            :attr:`~.ops_map` lookup fails, the given ``operation``
            argument is returned.

    """
    try:
        operation = operation.upper()
    except AttributeError:
        pass

    try:
        operation = ops_map[operation]()
    except KeyError:
        pass

    return operation


def _get_default_port(scheme):
    return 443 if scheme == 'https' else 9984


def _normalize_nodes(*nodes):
    if not nodes:
        return (DEFAULT_NODE,)
    norm_nodes = []
    for node in nodes:
        if not node:
            norm_nodes.append(DEFAULT_NODE)
            continue
        elif '://' not in node:
            node = '//{}'.format(node)
        parts = urlparse(node, scheme='http', allow_fragments=False)
        port = parts.port if parts.port else _get_default_port(parts.scheme)
        netloc = '{}:{}'.format(parts.hostname, port)
        norm_nodes.append(
            urlunparse((parts.scheme, netloc, parts.path, '', '', '')))

    return tuple(norm_nodes,)
