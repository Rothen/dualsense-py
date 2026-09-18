from dualsensepy.readable_value import ButtonValue, ReadableValue


def test_set_value_notifies_only_on_change():
    rv = ReadableValue(0)
    received: list[int] = []
    rv.subscribe(received.append)

    assert rv.set_value(0) is False
    assert rv.set_value(1) is True
    assert rv.set_value(1) is False

    assert received == [1]
    assert rv.value == 1


def test_force_value_always_notifies():
    rv = ReadableValue(5)
    received: list[int] = []
    rv.subscribe(received.append)

    rv.force_value(5)
    rv.force_value(5)

    assert received == [5, 5]
    assert rv.value == 5


def test_subscribers_can_dispose():
    rv = ReadableValue(0)
    received: list[int] = []
    disposable = rv.subscribe(received.append)

    rv.set_value(1)
    disposable.dispose()
    rv.set_value(2)

    assert received == [1]


def test_button_value_starts_unpressed():
    button = ButtonValue()

    assert button.value is False


def test_button_value_fires_pressed_and_released_on_change():
    button = ButtonValue()
    pressed: list[bool] = []
    released: list[bool] = []
    button.pressed(lambda: pressed.append(True))
    button.released(lambda: released.append(True))

    button.set_value(True)
    button.set_value(True)  # no change, must not fire again
    button.set_value(False)

    assert pressed == [True]
    assert released == [True]


def test_button_value_force_value_fires_every_call():
    button = ButtonValue()
    pressed: list[int] = []
    button.pressed(lambda: pressed.append(True))

    button.force_value(True)
    button.force_value(True)

    assert pressed == [True, True]
