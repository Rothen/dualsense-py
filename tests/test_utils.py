from unittest.mock import Mock
from pytest import MonkeyPatch

import dualsensepy.utils as utils_module
from dualsensepy.backends.backend import Backend
from dualsensepy.dual_sense_controller import DualSenseController


def test_get_all_controllers_wraps_each_device_info(monkeypatch: MonkeyPatch):
    device_infos = [Mock(), Mock()]
    seen_args = {}

    def fake_get_all_device_infos(vendor_id: int, product_id: int):
        seen_args["args"] = (vendor_id, product_id)
        return device_infos

    monkeypatch.setattr(utils_module, "get_all_device_infos", fake_get_all_device_infos)

    controllers = utils_module.get_all_controllers(0x1234, 0x5678)

    assert seen_args["args"] == (0x1234, 0x5678)
    assert len(controllers) == len(device_infos)
    assert all(isinstance(c, DualSenseController) for c in controllers)


def test_get_all_dual_sense_controllers_uses_sony_vendor_and_product_ids(monkeypatch: MonkeyPatch):
    def fake_get_all_controllers(vendor_id: int, product_id: int) -> tuple[int, int]:
        return vendor_id, product_id

    monkeypatch.setattr(
        utils_module,
        "get_all_controllers",
        fake_get_all_controllers,
    )

    result = utils_module.get_all_dual_sense_controllers()

    assert result == (utils_module.SONY_VENDOR_ID, utils_module.DS_PRODUCT_ID)


def test_get_all_xbox_360_controllers_uses_microsoft_vendor_and_product_ids(monkeypatch: MonkeyPatch):
    def fake_get_all_controllers(vendor_id: int, product_id: int) -> tuple[int, int]:
        return vendor_id, product_id

    monkeypatch.setattr(
        utils_module,
        "get_all_controllers",
        fake_get_all_controllers,
    )

    result = utils_module.get_all_xbox_360_controllers()

    assert result == (utils_module.MS_VENDOR_ID, utils_module.XBOX_CONTROLLER_PRODUCT_ID)


def test_get_available_controllers_wraps_devices_from_the_active_backend(monkeypatch: MonkeyPatch):
    device_infos = [Mock(), Mock()]

    class FakeBackend:
        @staticmethod
        def _get_available_devices():
            return device_infos

    monkeypatch.setattr(Backend, "ActiveBackend", FakeBackend)

    controllers = utils_module.get_available_controllers()

    assert len(controllers) == len(device_infos)
    assert all(isinstance(c, DualSenseController) for c in controllers)
