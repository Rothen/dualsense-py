# type: ignore
from __future__ import annotations
import ctypes

from sdl3 import *

from ..device_infos import DeviceInfo
from ...mapping import create_orientation
from ...readable_value import ButtonValue
from ...states import (
    Accelerometer,
    Battery,
    Gyroscope,
    JoyStick,
    Orientation,
    TouchFinger,
    TriggerFeedback
)

deadzone: float = 0.1


class SDL3DeviceInfo(DeviceInfo[SDL_JoystickID, SDL_JoystickID]):

    __slots__ = (
        "__sdl_opened_gamepad",
        "__button_map",
    )

    def __init__(self, device_id: SDL_JoystickID):
        super().__init__(device_id)
        self.__sdl_opened_gamepad: SDL_POINTER[SDL_Gamepad] | None = None
        self.__button_map: list[tuple[int, ButtonValue]] = [
            (SDL_GAMEPAD_BUTTON_SOUTH, self._cross),
            (SDL_GAMEPAD_BUTTON_EAST, self._circle),
            (SDL_GAMEPAD_BUTTON_WEST, self._square),
            (SDL_GAMEPAD_BUTTON_NORTH, self._triangle),
            (SDL_GAMEPAD_BUTTON_BACK, self._share),
            (SDL_GAMEPAD_BUTTON_GUIDE, self._ps),
            (SDL_GAMEPAD_BUTTON_START, self._options),
            (SDL_GAMEPAD_BUTTON_LEFT_STICK, self._l3),
            (SDL_GAMEPAD_BUTTON_RIGHT_STICK, self._r3),
            (SDL_GAMEPAD_BUTTON_LEFT_SHOULDER, self._l1),
            (SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER, self._r1),
            (SDL_GAMEPAD_BUTTON_DPAD_UP, self._dpad_up),
            (SDL_GAMEPAD_BUTTON_DPAD_DOWN, self._dpad_down),
            (SDL_GAMEPAD_BUTTON_DPAD_LEFT, self._dpad_left),
            (SDL_GAMEPAD_BUTTON_DPAD_RIGHT, self._dpad_right),
            (SDL_GAMEPAD_BUTTON_MISC1, self._mikrophone),
            (SDL_GAMEPAD_BUTTON_TOUCHPAD, self._touch),
        ]

    def open(self):
        self.__sdl_opened_gamepad = SDL_OpenGamepad(self._orig_device_info)
        SDL_SetGamepadSensorEnabled(self.__sdl_opened_gamepad, SDL_SENSOR_ACCEL, True)
        SDL_SetGamepadSensorEnabled(self.__sdl_opened_gamepad, SDL_SENSOR_GYRO, True)

    def close(self):
        if self.__sdl_opened_gamepad is None:
            return

        self.set_led(0, 0, 0)
        SDL_CloseGamepad(self.__sdl_opened_gamepad)

    def _read(self):
        # Deliberately polls gamepad state instead of draining the SDL event
        # queue: SDL_PollEvent()/SDL_PumpEvents() may only be called from the
        # thread that initialized SDL, but DeviceInfo.read() runs on
        # DualSenseController's dedicated background thread. SDL_UpdateGamepads()
        # and the SDL_GetGamepad*() getters are documented as safe to call from
        # any thread.
        if self.__sdl_opened_gamepad is None:
            return
        
        SDL_UpdateGamepads()

        self.__read_buttons()
        self.__read_left_stick()
        self.__read_right_stick()
        self.__read_triggers()
        self.__read_sensors()

    def write(self):
        """
        Write data to the device.
        """
        pass

    def __read_buttons(self) -> None:
        for button, value in self.__button_map:
            value.set_value(bool(SDL_GetGamepadButton(self.__sdl_opened_gamepad, button)))

    def __read_axis(self, axis: int) -> float:
        raw_value = SDL_GetGamepadAxis(self.__sdl_opened_gamepad, axis)
        value = ((raw_value + 32768) / 65535.0) * 2 - 1
        return 0.0 if abs(value) < deadzone else value

    def __read_left_stick(self) -> None:
        x = self.__read_axis(SDL_GAMEPAD_AXIS_LEFTX)
        y = self.__read_axis(SDL_GAMEPAD_AXIS_LEFTY)
        self._left_joy_stick.set_value(JoyStick(x, y))

    def __read_right_stick(self) -> None:
        x = self.__read_axis(SDL_GAMEPAD_AXIS_RIGHTX)
        y = self.__read_axis(SDL_GAMEPAD_AXIS_RIGHTY)
        self._right_joy_stick.set_value(JoyStick(x, y))

    def __read_triggers(self) -> None:
        l2_value = SDL_GetGamepadAxis(self.__sdl_opened_gamepad, SDL_GAMEPAD_AXIS_LEFT_TRIGGER) / 32767.0
        r2_value = SDL_GetGamepadAxis(self.__sdl_opened_gamepad, SDL_GAMEPAD_AXIS_RIGHT_TRIGGER) / 32767.0
        self._l2_trigger.set_value(l2_value)
        self._r2_trigger.set_value(r2_value)
        self._l2.set_value(l2_value == 1.0)
        self._r2.set_value(r2_value == 1.0)

    def __read_sensors(self) -> None:
        accel_data = (ctypes.c_float * 3)()
        if SDL_GetGamepadSensorData(self.__sdl_opened_gamepad, SDL_SENSOR_ACCEL, accel_data, 3):
            self._accelerometer.set_value(Accelerometer(accel_data[0], accel_data[1], accel_data[2]))

        gyro_data = (ctypes.c_float * 3)()
        if not SDL_GetGamepadSensorData(self.__sdl_opened_gamepad, SDL_SENSOR_GYRO, gyro_data, 3):
            return

        self._gyroscope.set_value(Gyroscope(gyro_data[0], gyro_data[1], gyro_data[2]))

        dt = (self._read_time - self._last_read_time) if self._last_read_time else 0.0
        self._orientation.set_value(
            create_orientation(self._orientation.value, self._accelerometer.value, self._gyroscope.value, dt)
        )

    def set_led(self, r: int, g: int, b: int) -> bool:
        return SDL_SetGamepadLED(self.__sdl_opened_gamepad, r, g, b)
