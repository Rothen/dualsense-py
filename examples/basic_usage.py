"""Connect to the first DualSense controller, print button and stick events,
report battery level, and flash the light bar while the script runs.

Usage:
    python examples/basic_usage.py
"""

import sys
import time

from dualsensepy import DualSenseController
from dualsensepy.backends import SDL3Backend
from dualsensepy.states import Battery, JoyStick
from dualsensepy.utils import get_available_controllers


def print_stick(name: str, stick: JoyStick) -> None:
    print(f"{name}: x={stick.x:.2f} y={stick.y:.2f}")


def print_battery(battery: Battery) -> None:
    status = "charging" if battery.charging else "on battery"
    print(f"Battery: {battery.level_percentage:.0f}% ({status})")


def main() -> int:
    SDL3Backend.init()
    controllers = get_available_controllers()
    if not controllers:
        print("No DualSense controller found.", file=sys.stderr)
        return 1

    controller: DualSenseController = controllers[0]
    controller.open()

    controller.square_pressed(lambda: print("Square pressed"))
    controller.square_released(lambda: print("Square released"))
    controller.cross_pressed(lambda: print("Cross pressed"))
    controller.circle_pressed(lambda: print("Circle pressed"))
    controller.triangle_pressed(lambda: print("Triangle pressed"))
    controller.ps_pressed(lambda: print("PS pressed"))

    controller.left_joy_stick_changed(lambda stick: print_stick("Left stick", stick))
    controller.right_joy_stick_changed(lambda stick: print_stick("Right stick", stick))
    controller.battery_changed(print_battery)

    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    print("Connected. Press Ctrl+C to exit.")

    try:
        while True:
            for color in colors:
                controller.set_led(*color)
                time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        controller.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
