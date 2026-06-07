# pytest_selenium_framework
A homemade Python pytest + selenium test framework example
* pytest + selenium test framework using test functions and classes.
* How to test a list of browsers for the same function (not copy & paste function/class)
* Page object model
* Take screenshots on exception, e.g., cannot find an element. Note not on assert failure.
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

# Limitation
It does not show embedded screenshots in HTML reports, which can be resolved by using [pytest-selenium plugin](https://pytest-selenium.readthedocs.io/en/latest/) and you can find an equivalent example in another repository [here](https://github.com/peterjpxie/pytest-selenium_plugin_examples). Also, it automatically take screenshots on assert failure. 


