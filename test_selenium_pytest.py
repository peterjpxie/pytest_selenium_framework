"""
Install:
pip3 install -r requirements.txt 

Run:
pytest

see pytest.ini for more options.

Notes:
- Exceptions will cause test to fail and terminate just as assert.

Selenium timeouts:
1/ driver.get(url): No timeout, it will try to load all elements of the page fully, blocking.
    You can try to a timeout by driver.set_page_load_timeout(X), but it will raise an TimeoutException and fail the test if timeouts.
2/ driver.find_element(): Implicit wait, it will wait for the element to load before raising NoSuchElementException.
    driver.implicitly_wait(X)
3/ WebDriverWait(driver, X).until(expected_conditions.title_is('xxx')): wait for a condition like title match before raising an exception.
    Some attributes of a driver like tltle, url, etc. are not updated immediately after loading a new page, 
    so we need to wait for a while before checking them, and the implicit wait cannot be used here.

Tricks:
1/ Always maximize window on setup by drive.maximize_window().
    Reason: Some responsive website have dynamic xpath / css for elements. e.g., xpath you see in chrome dev tool in full window 
    could be different when the window size is smaller during tests.
"""
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import logging
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By       
from selenium.webdriver.support.events import EventFiringWebDriver
from selenium.webdriver.support.events import AbstractEventListener
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import inspect

# time to wait for get method to load a page completely before raising TimeoutException
TIMEWAIT_PAGE_LOAD_GET = 60
# explicit wait time in secs after loading a new page to check page match with driver.title.
TIMEWAIT_PAGE_LOAD = 15
# timeout for elements to load
TIMEWAIT_ELEMENT_LOAD = TIMEWAIT_PAGE_LOAD

# !!!!! This logging.basicConfig will also change selenium logging outputs. Set level DEBUG for debugging selenium !!!!!
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

# Notes:
#    - To use function without class, use 'global' browser scope across functions.
def setup_function():
    log.info('Setup function')
    global browser
    browser = webdriver.Chrome()

def teardown_function():
    log.info('Teardown function')
    global browser
    browser.quit()
    
def test_seleniumhq_homepage(request):
    # print test function name
    log.info("test_func %s:" % request.node.name)
    # Output: test_func test_seleniumhq_homepage:
    global browser
    browser.get('https://www.selenium.dev/')
    assert 'Selenium' in browser.title

# disable yahoo search test as yahoo search is not available in some countries.
def _test_yahoo_search(request):
    log.info("test_func %s:" % request.node.name)
    global browser
    browser.get('http://www.yahoo.com')
    assert 'Yahoo' in browser.title
    
    elem = browser.find_element(By.NAME,'p')  # Find the search box
    elem.send_keys('seleniumhq' + Keys.RETURN) 
    sleep(2)     

class TestPythonOrgChrome():
    def setup(self):
        log.info('Setting up browser...')
        self.wd = webdriver.Chrome() # webdriver.Firefox()
        # set viewport / window size
        self.wd.set_window_size(1024, 800)
 
    def teardown(self):
        log.info('tearing down browser...')
        self.wd.quit()
        
    def test_python_homepage(self):
        self.wd.get('https://www.python.org/')
        assert 'Welcome to Python.org' == self.wd.title  
        sleep(2)

# Test with a list of browsers, and headless mode
# Design:
#   Define own setup / teardown function so we can assign browser as argument.

# Define browsers you want to test, you can read from a config file as well.
#browser_list = ['Firefox','Chrome']
browser_list = ['Chrome']
class TestPythonOrgMultiDrivers():
    def setupOwn(self,browser):
        log.info('Setting up browser...')
        try:
            if str(browser).lower() == 'firefox':
                self.wd = webdriver.Firefox()
                # To run headless mode in Firefox, add below options.                
                '''
                vOptions = webdriver.firefox.options.Options()
                vOptions.headless = True 
                self.wd = webdriver.Firefox(options=vOptions)
                '''
            else:
                self.wd = webdriver.Chrome()
                # To run headless mode, i.e. no UI, add below options.
                # And you can ignore this error (no impact):  [0101/115120.672:ERROR:gpu_process_transport_factory.cc(967)] Lost UI shared context.
                '''
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")
                options.add_argument("--disable-gpu")
                self.wd = webdriver.Chrome(chrome_options=options)
                '''
        except:
            log.info('Failed to setup browser.')
 
    def teardownOwn(self):
        log.info('tearing down browser...')
        self.wd.quit()
        
    # We need the default teardown function so that the browser can be closed in case of test assert failure, in which test function is terminated and teardownOwn won't be executed. 
    def teardown(self):
        log.info('teardown::tearing down browser...')
        # self.wd.service.process == None if quit already.
        if self.wd.service.process != None:
            self.wd.quit()  
            
    def test_python_homepage(self):
        for browser in browser_list: 
            self.setupOwn(browser)
            self.wd.get('https://www.python.org/')
            assert 'Welcome to Python.org' == self.wd.title   
            self.teardownOwn()


# Page Object Model            
class TestPythonOrgPageModel():
    def setupOwn(self,browser):
        log.info('Setting up browser...')
        try:
            if str(browser).lower() == 'firefox':
                self.wd = webdriver.Firefox()
            else:
                self.wd = webdriver.Chrome()
        except:
            log.info('Failed to setup browser.')
        
        # taking screenshots on Exception,e.g. cannot find elements. But not in assert failure. 
        self.wd = EventFiringWebDriver(self.wd, ScreenshotListener())    
        self.wd.set_page_load_timeout(TIMEWAIT_PAGE_LOAD_GET)
        # set implicitly_wait for elements to load
        self.wd.implicitly_wait(TIMEWAIT_ELEMENT_LOAD)
        # self.wd.set_window_size(1024, 800)
        # some responsive website have dynamic xpath / css for elements, so it is better to max window unless testing diff win size on purpose.
        self.wd.maximize_window()        
  
    def teardownOwn(self):
        log.info('teardownOwn::tearing down browser...')
        self.wd.quit()
    
    # We need the default teardown function so that the browser can be closed in case of test assert failure, in which test function is terminated and teardownOwn won't be executed. 
    def teardown(self):
        log.info('teardown::tearing down browser...')
        # self.wd.service.process == None if quit already.
        if self.wd.service.process != None:
            self.wd.quit()    
        
    def test_python_homepage_pageObject(self):
        for browser in browser_list: 
            # Set up browser
            self.setupOwn(browser)
            
            # Test function
            self.wd.get('https://www.python.org/')
            homepage = PythonOrgHomepage(self.wd)
            # Always check if it is the right page first
            assert homepage.is_page_matched()
            # Test Validations 
            # assert homepage.getTitle() == 'Failed Title'
            pyPiHomepage = homepage.click_pypi()
            # Check it redirects to PyPi website.
            assert pyPiHomepage.is_page_matched()
            
            # Search by 'selenium' and check 1st result is selenium package.
            searchText = 'selenium'
            searchResultPage = pyPiHomepage.searchPackage(searchText)
            assert searchResultPage.is_page_matched()
            check_result_row = 1
            expected_resultText = 'selenium'
            actual_resultText = searchResultPage.getSearchResultText(check_result_row) 
            # self.wd.save_screenshot("screenshot_searchResult.png")
            if actual_resultText != expected_resultText:
                self.take_screenshot()
            assert actual_resultText == expected_resultText, 'search result not matched'
            # Tear down browser
            self.teardownOwn()
            
    def take_screenshot(self):
        class_name = self.__class__.__name__
        # This return caller function's name, not this function take_screenshot.
        caller_func_name = inspect.stack()[1][3]
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = "screenshot_" + class_name + '-' + caller_func_name + '_' + now + ".png"
        self.wd.save_screenshot(filename)


# Take screenshot on Exception,e.g. cannot find elements. But not in assert failure. However for assert failure you can control and take screenshot if needed.
# To take screenshot for both exception and assert failure, it seems we have to use unittest framework. Check below link:
# https://stackoverflow.com/questions/12024848/automatic-screenshots-when-test-fail-by-selenium-webdriver-in-python
# http://blog.likewise.org/2015/01/automatically-capture-browser-screenshots-after-failed-python-ghostdriver-tests/ 
class ScreenshotListener(AbstractEventListener):
    def on_exception(self, exception, driver):
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        screenshot_name = "screenshot_" + now + ".png"
        driver.save_screenshot(screenshot_name)
        log.info("Screenshot saved as '%s'" % screenshot_name)
# Usage example:
# self.wd = EventFiringWebDriver(self.wd, ScreenshotListener())    
 
# Page Object design
##################### 
# https://www.seleniumhq.org/docs/06_test_design_considerations.jsp#page-object-design-pattern (Java Example only)
# https://selenium-python.readthedocs.io/page-objects.html
# https://github.com/gunesmes/page-object-python-selenium
''' Principles
When a page is changed, you only need to change that page object, not the test functions.
Page objects themselves should never make verifications or assertions. 
There is one verification which can, and should, be within the page object and that is to verify that the page, and possibly critical elements on the page, were loaded correctly.
'''

# Base class is not necessary in my opinion, unless you have quite some common functions/variables. 
# Keep in simple. Please also refer to the java example in selenium org in 1st link.
class PythonOrgBase():
    def __init__(self, webdrive):
            self.wd = webdrive   
    # Optionally you can define common methods or class variables in base class.

# Inherit base page object
class PythonOrgHomepage_inheritBase(PythonOrgBase): 
    # Call this to verify if page is matched (1st check) right after initialization
    def is_page_matched(self):
        # Check if it is the right page by title
        # return self.wd.title == 'Welcome to Python.org'
        try:
            ret = WebDriverWait(self.wd, TIMEWAIT_PAGE_LOAD).until( EC.title_is('Welcome to Python.org' ))
        except:
            ret = False
        return ret

# Don't use base page object        
class PythonOrgHomepage(): 
    def __init__(self, webdrive):
        self.wd = webdrive   
    
    # Call this to verify if page is matched (1st check) right after initialization
    def is_page_matched(self):
        # Check if it is the right page by title
        # return self.wd.title == 'Welcome to Python.org'
        try:
            ret = WebDriverWait(self.wd, TIMEWAIT_PAGE_LOAD).until( EC.title_is('Welcome to Python.org' ))
        except:
            ret = False
        return ret
        
    def getTitle(self):
        return self.wd.title
    
    # return None if there are exceptions
    def click_pypi(self):
        # Catch find element failure to get better reading log prints 
        try:
            elem = self.wd.find_element(By.XPATH,'//*[@title="Python Package Index"]')
        except NoSuchElementException:
            log.info('Failed to locate PyPi link.')
            return None
            
        elem.click()
        return PyPiHomepage(self.wd)

class PyPiHomepage(): 
    def __init__(self, webdrive):
        self.wd = webdrive   
    
    def is_page_matched(self):
        # return self.wd.title == 'PyPI – the Python Package Index · PyPI'
        try:
            ret = WebDriverWait(self.wd, TIMEWAIT_PAGE_LOAD).until( EC.title_is('PyPI · The Python Package Index' ))
        except:
            ret = False
        return ret
        
    def searchPackage(self,searchText):       
        self.wd.find_element(By.ID,"search").clear()
        self.wd.find_element(By.ID,"search").send_keys("%s" % str(searchText).strip())
        self.wd.find_element(By.ID,"search").send_keys(Keys.ENTER)
        # wait for page to load, find an element on next page, order dropdown in this case. --- Removed and move to is_page_matched with wait-until function in next Page 
        # wait_element_nextPage = self.wd.find_element(By.XPATH,'//*[@id="order"]')
        return PyPiSearchResultPage(self.wd)

class PyPiSearchResultPage(): 
    def __init__(self, webdrive):
        self.wd = webdrive   
    
    def is_page_matched(self):
        log.info('Current page title:' + self.wd.title)
        # return self.wd.title == 'Search results · PyPI'
        try:
            ret = WebDriverWait(self.wd, TIMEWAIT_PAGE_LOAD).until(EC.title_is('Search results · PyPI' ))
        except:
            ret = False
        return ret
        
    
    # index starts with 1
    def getSearchResultText(self,index):
        self.result_index = index
        elem_found = True
        try:
            # Note: This xpath may change.
            self.elem = self.wd.find_element(By.XPATH,'//*[@id="content"]/div/div/div[2]/form/div[3]/ul/li[%s]/a/h3/span[1]' 
                                                      % self.result_index)
        except NoSuchElementException:
            log.info('Search result row not found.')
            elem_found = False
            return None   
        if elem_found == True:
            log.info('Found search result row.')
            log.info('element text: ' + self.elem.text)
            return self.elem.text

# Check exist by xpath        
def is_element_present_by_xpath(webdriver,xpath):
    try:
        webdriver.find_element(By.XPATH,xpath)
    except NoSuchElementException:
        return False
    return True

# A common check exist function    
# Example: is_element_present(browser,By.NAME,'username')    
def is_element_present(webdriver, byHow, byValue):
    try: 
        webdriver.find_element(byHow, byValue)
    except NoSuchElementException: 
        return False
    return True        
    
# Different Locators
# https://selenium-python.readthedocs.io/locating-elements.html
'''
Methods: 
find_element(By.X, "XX") - General, replace below deprecated methods.
find_element_by_id
find_element_by_name
find_element_by_xpath  -- Recommend this
find_element_by_link_text
find_element_by_partial_link_text
find_element_by_tag_name
find_element_by_class_name
find_element_by_css_selector  -- Don't like this because it has spaces in the path
find_elements  - Return a list IMO.

Inspectors:
Recommend Chrome than Firefox, because Chrome gives smarter xpath while Firefox gives full xpath.
For instance, inspect Donate button on Seleniumhq.org.
Chrome: //*[@id="sidebar"]/div[2]/form/input[3]
Firfox: /html/body/div[3]/div[2]/div[1]/div[2]/form/input[3]
'''

''' Example page:
<html>
 <body>
  <form id="loginForm">
   <input name="username" type="text" />
   <input name="password" type="password" />
   <input name="continue" type="submit" value="Login" />
   <input name="continue" type="button" value="Clear" />
  </form>
</body>
<html> 
'''
# To run this test, install a web host server, e.g. Fenix for windows, and host above HTML file, e.g. index.html.
# Then rename the function as test_locators().
def disabled_test_locators():
    global browser
    # wd.get('https://www.seleniumhq.org/')
    browser.get('http://127.0.0.1:8000/')        
    elem_found = True
    try:
        elem = browser.find_element(By.ID,'loginForm')
        elem = browser.find_element(By.NAME, 'password')
        
        # Below all find the same form element
        login_form = browserwd.find_element(By.XPATH,"/html/body/form")
        login_form = browserwd.find_element(By.XPATH,"/html/body/form[1]")
        login_form = browserwd.find_element(By.XPATH,"//form[1]")
        login_form = browserwd.find_element(By.XPATH,"//form[@id='loginForm']")
        login_form = browserwd.find_element(By.XPATH,"//*[@id='loginForm']")
        login_form = browserwd.find_element(By.XPATH,"//*[@id='loginForm'][1]")
        login_form = browserwd.find_element(By.XPATH,"//*[contains(@id,'login')]") # contains, yet to test
        
        # Below all find the same username element
        username_elem = browserwd.find_element(By.XPATH,"//input[@name='username']")
        username_elem = browserwd.find_element(By.XPATH,"//*[@name='username']")
        username_elem = browserwd.find_element(By.XPATH,"//*[@id='loginForm']/input[1]")
        
        # Find username input by general method find_element with a locator, a tuple of ByHow and value, as argument.
        username_elem = browser.find_element(By.XPATH,"//*[@id='loginForm']/input[1]")
        username_elem = browser.find_element(By.NAME,"username")
        
        # Find element by text
        text_elem = browserwd.find_element(By.XPATH,"//*[text()='Simple page']") # Exact match 
        text_elem = browserwd.find_element(By.XPATH,"//*[contains(text(),'Simple')]") # contain
        # Find element by value
        submit_button = browserwd.find_element(By.XPATH,"//*[@value='Login']")  
        clear_button = browserwd.find_element(By.XPATH,"//input[@value='Clear']") 
        
        ''' These are the attributes available for By class:
        ID = "id"
        XPATH = "xpath"
        LINK_TEXT = "link text"
        PARTIAL_LINK_TEXT = "partial link text"
        NAME = "name"
        TAG_NAME = "tag name"
        CLASS_NAME = "class name"
        CSS_SELECTOR = "css selector"
        '''                
    except NoSuchElementException:
        log.info('Element not found.')
        elem_found = False      # If using 'assert false' inside except, it prints a lot of debug logs in failure, not wanted.
    if elem_found == False:
        assert False
    else:
        log.info('Found element.')
        username_elem.send_keys('Peter')    
        
    sleep(1)

    
