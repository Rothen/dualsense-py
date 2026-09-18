import pytest
from typing import Any

from dualsensepy.backends.device_infos import DeviceInfo


class FakeDeviceInfo(DeviceInfo[Any, Any]):
    """In-memory DeviceInfo double that lets tests drive a DualSenseController
    by setting state values directly, without any real HID hardware."""

    def __init__(self):
        super().__init__(orig_device_info=None)
        self.open_calls = 0
        self.close_calls = 0
        self.before_start_calls = 0
        self.read_calls = 0
        self.write_calls = 0
        self.led_calls: list[tuple[int, int, int]] = []

    def open(self):
        self.open_calls += 1

    def close(self):
        self.close_calls += 1

    def before_start(self):
        self.before_start_calls += 1

    def _read(self):
        self.read_calls += 1

    def write(self):
        self.write_calls += 1

    def set_led(self, r: int, g: int, b: int) -> None:
        self.led_calls.append((r, g, b))


@pytest.fixture
def fake_device_info() -> FakeDeviceInfo:
    return FakeDeviceInfo()
