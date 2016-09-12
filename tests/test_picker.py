from pytest import raises


def test_round_robin_picker_raises_on_no_connections():
    from bigchaindb_driver.picker import RoundRobinPicker
    from bigchaindb_driver.exceptions import ConnectionError
    with raises(ConnectionError):
        RoundRobinPicker()

def test_round_robin_picker_cycles():
    from bigchaindb_driver.picker import RoundRobinPicker
    url_1 = 'url1'
    url_2 = 'url0'

    picker = RoundRobinPicker(url_1, url_2)
    connection = picker.pick()
    assert connection == url_1
    connection = picker.pick()
    assert connection == url_2
    # Loops back to give first instance again
    connection = picker.pick()
    assert connection == url_1


def test_round_robin_picker_iters():
    from bigchaindb_driver.picker import RoundRobinPicker
    url_1 = 'url1'
    url_2 = 'url0'

    picker = RoundRobinPicker(url_1, url_2)
    connection = next(picker)
    assert connection == url_1
    connection = next(picker)
    assert connection == url_2
    # Loops back to give first instance again
    connection = next(picker)
    assert connection == url_1
