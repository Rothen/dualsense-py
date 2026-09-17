# DualSense Controller Python Library (DS-PY)

This project provides a Python library for interacting with DualSense controllers. It supports reading input states, managing device connections, and controlling features like LEDs and trigger feedback.

## Features

- **Input State Reading**: Access data from buttons, joysticks, accelerometers, gyroscopes, and touchpads.
- **Device Management**: Detect and manage connected DualSense controllers.
- **LED Control**: Set the LED colors on the controller.
- **Trigger Feedback**: Configure adaptive trigger feedback modes.
- **Cross-Platform Support**: Includes backends for both `hidapi` and `SDL3`.

## Installation

Install from PyPI:

```bash
pip install dualsensepy
```

Or install from source:

```bash
git clone https://github.com/Rothen/dualsensepy.git
cd dualsensepy
pip install .
```

## Usage

### Detecting Controllers

Use the utility functions to detect connected controllers:

```python
from dualsensepy.utils import get_all_dual_sense_controllers

controllers = get_all_dual_sense_controllers()
if controllers:
    print(f"Found {len(controllers)} DualSense controller(s).")
else:
    print("No DualSense controllers found.")
```

### Reading Input States

```python
from dualsensepy.dual_sense_controller import DualSenseController

controller = controllers[0]
controller.open()

def on_square_pressed():
    print("Square button pressed!")

controller.square_pressed(on_square_pressed)
```

### Setting LED Colors

```python
controller.set_led(255, 0, 0)  # Set LED to red
```

### Closing the Controller

```python
controller.close()
```

## Backends

This library supports multiple backends for device communication:

- **HIDAPI**: Provides low-level access to USB devices.
- **SDL3**: Offers cross-platform support for game controllers.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the [MIT License](LICENSE.txt).
