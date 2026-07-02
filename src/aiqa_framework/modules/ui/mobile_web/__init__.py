"""Playwright mobile-web emulation (reuses the web POM).

Mobile-web = the same Playwright web tests run under a device viewport / user
agent / touch via Playwright device descriptors. Native mobile (Appium) is a
separate surface: ``modules/mobile``.
"""

from __future__ import annotations

from typing import Any

from playwright.sync_api import Playwright

DEFAULT_DEVICE = "Pixel 5"


def device_context_args(playwright: Playwright, device: str = DEFAULT_DEVICE) -> dict[str, Any]:
    """``browser_context_args`` for a Playwright device descriptor (viewport, UA, touch)."""
    descriptor = playwright.devices.get(device)
    if descriptor is None:
        raise ValueError(f"unknown Playwright device {device!r}")
    return dict(descriptor)


__all__ = ["DEFAULT_DEVICE", "device_context_args"]
