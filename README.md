# pytest_selenium_framework
A homemade Python pytest + selenium test framework example
* pytest + selenium test framework using test functions and classes.
* How to test a list of browsers for the same function (not copy & paste function/class)
* Page object model
* Take screenshots on test failure, e.g., cannot find an element, assert failure etc.
* Implicit wait and explicit wait for loading pages or elements.
* HTML reports

# Set up
1. Install Python3
2. Install required packages by pip (pip3 in Linux)

```
pip install -r requirements.txt
```

Note: Since selenium 4.12, it will auto download browser drivers on 1st run.

# Run
List test cases:
```
pytest --collectonly -q
```

Run all tests:
```
pytest
```

Run with HTML report:
```
pytest -v --html=report.html --self-contained-html
```

More options are defined in pytest.ini or you can overwrite in CLI parameters.

# Screenshots in HTML report
Screenshots taken via `ScreenshotListener` (on WebDriver exceptions) or on test failures are automatically embedded in the pytest-html report (works with `--self-contained-html`).

This is implemented via a `pytest_runtest_makereport` hook in [conftest.py](conftest.py) that attaches `driver.get_screenshot_as_base64()` using `pytest_html.extras.png(...)`. 

Note: You can also use [pytest-selenium](https://pytest-selenium.readthedocs.io/en/latest/) plugin to achieve the same.

