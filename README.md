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

`pip install -U pytest selenium pytest-html` 

or

`pip install -r requirements.txt`

3. Download WebDriver executables

Download WebDriver executables for your respective browsers under test, e.g. [chromedriver](https://chromedriver.chromium.org/downloads), [Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/) and [Firefox webdriver](https://github.com/mozilla/geckodriver/releases), to a path (e.g. d:/webdriver/) and add this path to system path so that the WebDriver executables can be called anywhere.  

# Run
Download the code, and run 'pytest' in the same folder.

`pytest`

Run with HTML report:

`pytest -v --html=report.html --self-contained-html` 

More options are defined in pytest.ini or you can overwrite in CLI parameters.

# Limitation
It does not show embedded screenshots in HTML reports, which can be resolved by using [pytest-selenium plugin](https://pytest-selenium.readthedocs.io/en/latest/) and you can find an equivalent example in another repository [here](https://github.com/peterjpxie/pytest-selenium_plugin_examples). Also, it automatically take screenshots on assert failure. 


