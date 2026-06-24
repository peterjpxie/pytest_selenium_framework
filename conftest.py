"""
Support for embedding screenshots in pytest-html report.

Works with --self-contained-html because we pass base64 content.
"""
import pytest
from pytest_html import extras
import logging

log = logging.getLogger(__name__)


def _get_driver_from_item(item):
    """Try multiple ways to retrieve the webdriver from test item.
    Supports:
      - Class based tests using self.wd (setup_method style)
      - Global "browser"
      - funcargs if someone uses a "driver" fixture
    """
    # Class instance style: def setup_method(self): self.wd = ...
    if hasattr(item, "instance"):
        driver = getattr(item.instance, "wd", None)
        if driver is not None:
            return driver

    # pytest function style or injected
    if hasattr(item, "funcargs"):
        for key in ("wd", "driver", "browser", "selenium"):
            d = item.funcargs.get(key)
            if d is not None:
                return d

    # Legacy global used in some tests here
    try:
        import test_selenium_pytest as tmod
        if hasattr(tmod, "browser"):
            return tmod.browser
    except Exception:
        pass

    return None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach screenshot (as base64) to the report when test fails.

    This makes screenshots appear embedded inside the HTML report
    even with --self-contained-html.
    """
    outcome = yield
    report = outcome.get_result()

    # We only care about failures during the actual test call (not setup/teardown)
    if report.when != "call":
        return

    if not report.failed:
        return

    driver = _get_driver_from_item(item)
    if driver is None:
        return

    try:
        # Prefer the exact screenshot captured by ScreenshotListener (on_exception)
        screenshot_base64 = getattr(driver, "_last_screenshot_base64", None)

        # Fall back to taking one now (covers assert failures, and tests without the listener)
        if not screenshot_base64:
            screenshot_base64 = driver.get_screenshot_as_base64()

        # Use the modern report.extras list (pytest-html >= 2/3/4)
        extra = getattr(report, "extras", [])
        # extras.png(base64) is a convenience for image(..., mime_type=image/png)
        extra.append(extras.png(screenshot_base64, name="Screenshot"))
        report.extras = extra

        log.info("Attached screenshot to HTML report for failed test: %s", item.nodeid)
    except Exception as e:
        # Don't let screenshot failure break the report
        log.warning("Failed to attach screenshot to report: %s", e)
