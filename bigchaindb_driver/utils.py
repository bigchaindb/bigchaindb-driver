"""Set of utilities to support various functionalities of the driver.

Attributes:
    ops_map (dict): Mapping between operation strings and classes.
        E.g.: The string ``'CREATE'`` is mapped to
        :class:`~.CreateOperation`.
"""


class CreateOperation:
    """Class representing the ``'CREATE'`` transaction operation."""


class TransferOperation:
    """Class representing the ``'TRANSFER'`` transaction operation."""


ops_map = {
    'CREATE': CreateOperation,
    'TRANSFER': TransferOperation,
}


def _normalize_operation(operation):
    """
    Normalizes the given operation string. For now, this simply means
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
