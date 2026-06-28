"""
Support for embedding screenshots in pytest-html report.

Works with --self-contained-html because we pass base64 content.
"""
import pytest
from pytest_html import extras
import logging

# !!!!! don't directly call logging.basicConfig as it will also change selenium logging outputs. Set level DEBUG for debugging selenium !!!!!
# %(levelname)7s to align 7 bytes to right, %(levelname)-7s to left.
common_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)-7s][%(lineno)-3d]: %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S",
)

# Note: To create multiple log files, must use different logger name.
def setup_logger(log_file, level=logging.INFO, name="", formatter=common_formatter):
    """Function setup as many loggers as you want."""
    handler = logging.FileHandler(log_file, mode="w")  # default mode is append
    # Or use a rotating file handler
    # handler = RotatingFileHandler(log_file,maxBytes=1024, backupCount=5)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

# default debug logger
log = setup_logger("debug.log", logging.INFO, name=__name__)


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
    
    This function is called for every test phase ('setup', 'call', 'teardown').
    'item'  -> the collected test function
    'call'  -> the CallInfo object for that phase
    """
    # fixture to get test result
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

        # Use the modern report.extras list (pytest-html >= 4.0.0)
        new_extras = getattr(report, "extras", [])
        # extras.png(base64) is a convenience for image(..., mime_type=image/png)
        new_extras.append(extras.png(screenshot_base64, name="Screenshot"))
        report.extras = new_extras
        # Note this log won't be captured in the pytest outputs as this function is defined in the hook
        log.info("Attached screenshot to HTML report for failed test: %s", item.nodeid)
    except Exception as e:
        # Don't let screenshot failure break the report
        log.warning("Failed to attach screenshot to report: %s", e)
