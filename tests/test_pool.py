from unittest.mock import Mock


def test_pool_factory(mock_picker):
    from bigchaindb_driver.pool import Pool
    from .utils import create_mock_connection
    url_0 = 'url0'
    url_1 = 'url1'
    extra_arg_1 = 'extra_arg_1'
    extra_arg_2 = 'extra_arg_2'

    # Set up class mocks (2 connection instances, and one picker)
    mock_connection_cls = Mock()
    mock_connection_instance_0 = create_mock_connection()
    mock_connection_instance_1 = create_mock_connection()
    mock_connection_cls.side_effect = [
        mock_connection_instance_0,
        mock_connection_instance_1
    ]
    mock_picker.return_value = mock_picker

    pool = Pool.connect(url_0, url_1, connection_cls=mock_connection_cls,
                        picker_cls=mock_picker, extra_arg_1=extra_arg_1,
                        extra_arg_2=extra_arg_2)
    assert len(pool.connections) == 2
    assert pool.connections[0] == mock_connection_instance_0
    assert pool.connections[1] == mock_connection_instance_1
    assert pool.picker == mock_picker

    mock_connection_cls_call_list = mock_connection_cls.call_args_list
    assert len(mock_connection_cls_call_list) == 2
    assert mock_connection_cls_call_list[0] == ((url_0,), {
        'extra_arg_1': extra_arg_1,
        'extra_arg_2': extra_arg_2,
    })
    assert mock_connection_cls_call_list[1] == ((url_1,), {
        'extra_arg_1': extra_arg_1,
        'extra_arg_2': extra_arg_2,
    })

    assert mock_picker.call_count == 1
    mock_picker.assert_called_with(
        mock_connection_instance_0,
        mock_connection_instance_1)


def test_default_picker():
    from bigchaindb_driver.pool import Pool
    from .utils import create_mock_connection
    url_0 = 'url0'
    url_1 = 'url1'

    # Set up connection mocks (2 instances)
    mock_connection_cls = Mock()
    mock_connection_instance_0 = create_mock_connection()
    mock_connection_instance_1 = create_mock_connection()
    mock_connection_cls.side_effect = [
        mock_connection_instance_0,
        mock_connection_instance_1
    ]

    pool = Pool.connect(url_0, url_1, connection_cls=mock_connection_cls)
    connection = pool.get_connection()
    assert connection == mock_connection_instance_0
    connection = pool.get_connection()
    assert connection == mock_connection_instance_1
    # Loops back to give first instance again
    connection = pool.get_connection()
    assert connection == mock_connection_instance_0
