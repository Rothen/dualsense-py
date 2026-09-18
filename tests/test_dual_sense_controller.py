import time

from dualsense_py.dual_sense_controller import DualSenseController
from dualsense_py.states import Battery, JoyStick
from conftest import FakeDeviceInfo

def test_open_and_close_drive_the_device_lifecycle(fake_device_info: FakeDeviceInfo):
    controller = DualSenseController(fake_device_info)

    controller.open()
    time.sleep(0.05)
    controller.close()

    assert fake_device_info.open_calls == 1
    assert fake_device_info.before_start_calls == 1
    assert fake_device_info.read_calls > 0
    assert fake_device_info.close_calls == 1
    assert not controller.read_thread.is_alive()


def test_square_pressed_and_released_callbacks(fake_device_info: FakeDeviceInfo):
    controller = DualSenseController(fake_device_info)
    pressed: list[bool] = []
    released: list[bool] = []
    controller.square_pressed(lambda: pressed.append(True))
    controller.square_released(lambda: released.append(True))

    fake_device_info.square.set_value(True)
    fake_device_info.square.set_value(False)

    assert pressed == [True]
    assert released == [True]


def test_button_callback_does_not_fire_on_repeated_value(fake_device_info: FakeDeviceInfo):
    controller = DualSenseController(fake_device_info)
    events: list[str] = []
    controller.cross_pressed(lambda: events.append("pressed"))

    fake_device_info.cross.set_value(True)
    fake_device_info.cross.set_value(True)

    assert events == ["pressed"]


def test_left_joy_stick_changed_emits_the_new_value(fake_device_info: FakeDeviceInfo):
    controller = DualSenseController(fake_device_info)
    received: list[JoyStick] = []
    controller.left_joy_stick_changed(received.append)

    stick = JoyStick(x=0.5, y=-0.5)
    fake_device_info.left_joy_stick.set_value(stick)

    assert received == [stick]


def test_battery_changed_emits_the_new_value(fake_device_info: FakeDeviceInfo):
    controller = DualSenseController(fake_device_info)
    received: list[Battery] = []
    controller.battery_changed(received.append)

    battery = Battery(level_percentage=80.0, full=False, charging=True)
    fake_device_info.battery.set_value(battery)

    assert received == [battery]


def test_set_led_delegates_to_device_info(fake_device_info: FakeDeviceInfo):
    controller = DualSenseController(fake_device_info)

    controller.set_led(10, 20, 30)

    assert fake_device_info.led_calls == [(10, 20, 30)]


def test_disposing_a_subscription_stops_further_callbacks(fake_device_info: FakeDeviceInfo):
    controller = DualSenseController(fake_device_info)
    events: list[bool] = []
    disposable = controller.triangle_pressed(lambda: events.append(True))

    fake_device_info.triangle.set_value(True)
    disposable.dispose()
    fake_device_info.triangle.set_value(False)
    fake_device_info.triangle.set_value(True)

    assert events == [True]
