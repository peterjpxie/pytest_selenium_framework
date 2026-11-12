# pytest_selenium_framework
A homemade Python pytest + selenium test framework example
* pytest + selenium test framework using test functions and classes.
* How to test a list of browsers for the same function via `pytest.parametrize` in one run (not copy & paste function/class).
    Note: pytest-selenium plugin doesn't support running on multiple browsers in a test run.
* Take screenshots automatically and embed into html report on test failure, e.g., cannot find an element, assert failure etc.
* Page object model
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

# Config
- Headless
```
# off by default; environment variable HEADLESS=1 enables it
HEADLESS=1 pytest
```

# Notes
## Screenshots in HTML report
Screenshots taken via `ScreenshotListener` (on WebDriver exceptions) or on test failures are automatically embedded in the pytest-html report (works with `--self-contained-html`).

This is implemented via a `pytest_runtest_makereport` hook in [conftest.py](conftest.py) that attaches `driver.get_screenshot_as_base64()` using `pytest_html.extras.png(...)`. 

Note: You can also use [pytest-selenium](https://pytest-selenium.readthedocs.io/en/latest/) plugin to achieve the same.

## parametrize case order
For testing, it is preferred to run all tests with one browser then next browser as cases may have sequence dependency.
To achieve this order, we need to modify `pytest_collection_modifyitems()` in `conftest.py`.
See `test_paramtrize_seq.py` as a simple example to understand it.
```
# original out sequence:
test_paramtrize_seq.py::TestParamtrizeSeq::test_a[Chrome] PASSED  
test_paramtrize_seq.py::TestParamtrizeSeq::test_a[Firefox] PASSED 
test_paramtrize_seq.py::TestParamtrizeSeq::test_b[Chrome] PASSED  
test_paramtrize_seq.py::TestParamtrizeSeq::test_b[Firefox] PASSED  

# out sequence with pytest_collection_modifyitems() change in conftest.py:
test_paramtrize_seq.py::TestParamtrizeSeq::test_a[Chrome] PASSED  
test_paramtrize_seq.py::TestParamtrizeSeq::test_b[Chrome] PASSED  
test_paramtrize_seq.py::TestParamtrizeSeq::test_a[Firefox] PASSED 
test_paramtrize_seq.py::TestParamtrizeSeq::test_b[Firefox] PASSED 
```
Note: 
- You may be able to achieve the same result using `pytest_generate_tests`.
- I apply this re-ordering to explicit target classes defined in `PARAMTRIZED_CLASSES_TO_REORDER` in conftest.py but it is probably not needed and simply apply to all.
