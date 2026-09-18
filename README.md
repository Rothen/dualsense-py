# dualsense-py

A Python library for reading state from a DualSense controller and reacting to input events in real time.

This package exposes the controller as a live stream of events and state updates, with support for:

- button press/release callbacks
- analog stick changes
- trigger values
- accelerometer and gyroscope data
- battery and orientation state
- LED control
- HID-backed controller discovery

## Features

- Read DualSense button states with callback hooks such as `square_pressed()` and `circle_released()`
- Track joystick, trigger, accelerometer, gyroscope, and orientation values as they change
- Detect available controllers using built-in utility functions
- Set the controller LED color with `set_led(red, green, blue)`
- Use the library with native HID device support through `hidapi` and SDL-based discovery helpers

## Installation

Install from PyPI:

```bash
pip install dualsense-py
```

Install from the repository source:

```bash
git clone https://github.com/Rothen/dualsensepy.git
cd dualsensepy
pip install .
```

## Quick start

```python
import time

from dualsense_py.utils import get_all_dual_sense_controllers

controllers = get_all_dual_sense_controllers()
if not controllers:
    raise RuntimeError("No DualSense controller found")

controller = controllers[0]
controller.open()

controller.square_pressed(lambda _: print("Square pressed"))
controller.square_released(lambda _: print("Square released"))
controller.left_joy_stick_changed(lambda stick: print(f"Left stick: ({stick.x}, {stick.y})"))
controller.battery_changed(lambda battery: print(f"Battery: {battery.level_percentage}%"))
controller.set_led(0, 255, 0)

try:
    while True:
        time.sleep(0.1)
finally:
    controller.close()
```

A fuller, runnable version of this (button/stick/battery logging plus a light bar color cycle) lives at [examples/basic_usage.py](examples/basic_usage.py):

```bash
python examples/basic_usage.py
```

## Controller discovery

The package includes helper functions for locating controllers:

```python
from dualsense_py.utils import (
    get_all_controllers,
    get_all_dual_sense_controllers,
    get_available_controllers,
)

controllers = get_all_dual_sense_controllers()
for controller in controllers:
    print(controller)

# Generic discovery by vendor/product IDs
all_controllers = get_all_controllers(0x054C, 0x0CE6)
```

## Backends

`dualsense-py` ships two backends for talking to the controller:

- **hidapi** (`get_all_dual_sense_controllers()`, `get_all_controllers()`) — reads raw HID reports directly. This is the default used above and needs no extra setup. LED control (`set_led`) is not implemented on this backend yet and is a no-op.
- **SDL3** (`get_available_controllers()`) — uses SDL3's gamepad API for broader controller support and working LED control, at the cost of an explicit init step:

```python
from dualsense_py.backends import SDL3Backend
from dualsense_py.utils import get_available_controllers

SDL3Backend.init()
controllers = get_available_controllers()
```

Call `SDL3Backend.init()` once before discovering controllers with `get_available_controllers()`. Controller state is read by polling (`SDL_UpdateGamepads()` plus the `SDL_GetGamepad*()` getters) rather than draining SDL's event queue, since `DualSenseController` reads each device from its own background thread and SDL only allows event pumping from the thread that called `SDL_Init`.

## Event API

The controller exposes a set of event subscription methods. The naming follows the hardware input names and callback type.

### Button press callbacks

```python
controller.square_pressed(lambda _: print("Square pressed"))
controller.cross_pressed(lambda _: print("Cross pressed"))
controller.circle_pressed(lambda _: print("Circle pressed"))
controller.triangle_pressed(lambda _: print("Triangle pressed"))
controller.l1_pressed(lambda _: print("L1 pressed"))
controller.r1_pressed(lambda _: print("R1 pressed"))
controller.share_pressed(lambda _: print("Share pressed"))
controller.options_pressed(lambda _: print("Options pressed"))
```

### Button release callbacks

```python
controller.square_released(lambda _: print("Square released"))
controller.dpad_up_released(lambda _: print("D-pad up released"))
controller.dpad_down_released(lambda _: print("D-pad down released"))
controller.ps_released(lambda _: print("PS released"))
```

### State change callbacks

```python
controller.left_joy_stick_changed(lambda stick: print(stick))
controller.right_joy_stick_changed(lambda stick: print(stick))
controller.l2_trigger_changed(lambda value: print(f"L2: {value}"))
controller.r2_trigger_changed(lambda value: print(f"R2: {value}"))
controller.accelerometer_changed(lambda accel: print(accel))
controller.gyroscope_changed(lambda gyro: print(gyro))
controller.battery_changed(lambda battery: print(battery))
controller.orientation_changed(lambda orientation: print(orientation))
controller.touch_finger_1_changed(lambda finger: print(finger))
controller.touch_finger_2_changed(lambda finger: print(finger))
```

## State objects

The library emits dataclasses representing controller state values. These are the actual payloads produced by the change listeners:

- `JoyStick(x, y)`
- `Battery(level_percentage, full, charging)`
- `Accelerometer(x, y, z)`
- `Gyroscope(x, y, z)`
- `Orientation(pitch, roll, yaw)`
- `TouchFinger(active, id, x, y)`
- `TriggerFeedback(active, value)`

Example:

```python
controller.left_joy_stick_changed(
    lambda stick: print(f"X={stick.x}, Y={stick.y}")
)
```

## LED control

Set the light bar color on the controller:

```python
controller.set_led(255, 0, 0)    # red
controller.set_led(0, 255, 0)    # green
controller.set_led(0, 0, 255)    # blue
controller.set_led(255, 255, 0)  # yellow
```

The values are standard 8-bit channel values from 0 to 255.

> LED control currently requires the SDL3 backend — see [Backends](#backends). On the `hidapi` backend, `set_led` is a no-op.

## Runtime properties

The controller instance also exposes timing metadata while the read loop is running:

```python
print(controller.read_time)
print(controller.loop_time)
```

## Notes

- The project is currently in an early stage and is best treated as a low-level controller library.
- Controller access depends on the underlying HID / backend support in the current environment.
- Event callbacks are subscription-based and can be used to build reactive input loops or game automation logic.

## Development

Install the package with its test dependencies and run the test suite with `pytest`:

```bash
pip install -e .[dev]
pytest
```

The tests drive `DualSenseController` against an in-memory fake device (see `tests/conftest.py`), so no physical controller is required to run them.

## License

This project is licensed under the [MIT License](LICENSE.txt).

## Contributing

Contributions are welcome. If you want to improve the library, open an issue or submit a pull request with a clear description of the change and any validation steps.
