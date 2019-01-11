'''
Install:
pip3 install -U pytest
pip3 install -U selenium

Notes:
- Exceptions will cause test to fail and terminate just as assert.

'''
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

TIMEWAIT_PAGE_LOAD = 5

# !!!!! This logging.basicConfig will also change selenium logging outputs. Set level DEBUG for debugging selenium !!!!!
logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S')
log = logging.getLogger('')

''' 
Notes:
    - To use function without class, use 'global' browser scope across functions.
'''
def setup_function():
    log.info('Setup function')
    global browser
    browser = webdriver.Firefox()

def teardown_function():
    log.info('Teardown function')
    global browser
    browser.quit()
    
def test_seleniumhq_homepage(request):
    log.info("test_func %s:" % request.node.name)
    global browser
    browser.get('https://www.seleniumhq.org/')
    assert 'Selenium - Web Browser Automation' == browser.title

def test_yahoo_search(request):
    log.info("test_func %s:" % request.node.name)
    global browser
    browser.get('http://www.yahoo.com')
    assert 'Yahoo' in browser.title
    
    elem = browser.find_element_by_name('p')  # Find the search box
    elem.send_keys('seleniumhq' + Keys.RETURN) 
    sleep(2)     

class TestPythonOrgFirefox():
    def setup(self):
        log.info('Setting up browser...')
        self.wd = webdriver.Firefox()
 
    def teardown(self):
        log.info('tearing down browser...')
        self.wd.quit()
        
    def test_python_homepage(self):
        self.wd.get('https://www.python.org/')
        assert 'Welcome to Python.org' == self.wd.title   

# Test with a list of browsers
''' Design:
Define own setup / teardown function so we can assign browser as argument.
'''
# Define browsers you want to test, you can read from a config file as well.
#vBrowserList = ['Firefox','Chrome']
vBrowserList = ['Firefox']
class TestPythonOrg():
    def setupOwn(self,browser):
        log.info('Setting up browser...')
        try:
            if str(browser).lower() == 'firefox':
                self.wd = webdriver.Firefox()
                # To run headless mode in Firefox, add below options.                
                '''
                vOptions = webdriver.firefox.options.Options()
                vOptions.set_headless(True) 
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
        
    def test_python_homepage(self):
        for browser in vBrowserList: 
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
        # set implicitly_wait for elements to load
        self.wd.implicitly_wait(10)
  
    def teardownOwn(self):
        log.info('teardownOwn::tearing down browser...')
        self.wd.quit()
    
    # We need the default teardown function so that the browser can be closed in case of test assert failure, in which test function is terminated and teardownOwn won't be executed. 
    def teardown(self):
        log.info('teardown::tearing down browser...')
        # self.screenshot_on_failure()
        # self.wd.service.process == None if quit already.
        if self.wd.service.process != None:
            self.wd.quit()    
        
    def test_python_homepage_pageObject(self):
        for browser in vBrowserList: 
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
                assert False, 'search result not matched'
            # Tear down browser
            self.teardownOwn()
            
    def take_screenshot(self):
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.wd.save_screenshot("screenshot_" + now + ".png")
'''
Take screenshot on Exception,e.g. cannot find elements. But not in assert failure. However for assert failure you can control and take screenshot if needed.
To take screenshot for both exception and assert failure, it seems we have to use unittest framework. Check below link:
https://stackoverflow.com/questions/12024848/automatic-screenshots-when-test-fail-by-selenium-webdriver-in-python 
'''
# http://blog.likewise.org/2015/01/automatically-capture-browser-screenshots-after-failed-python-ghostdriver-tests/ 
class ScreenshotListener(AbstractEventListener):
    def on_exception(self, exception, driver):
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        screenshot_name = "screenshot_" + now + ".png"
        driver.save_screenshot(screenshot_name)
        print("Screenshot saved as '%s'" % screenshot_name)
# Usage example:
# self.wd = EventFiringWebDriver(self.wd, ScreenshotListener())    
 
# Page Object design 
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

#class PythonOrgHomepage(PythonOrgBase): 
       
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
            elem = self.wd.find_element_by_xpath('//*[@title="Python Package Index"]')
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
            ret = WebDriverWait(self.wd, TIMEWAIT_PAGE_LOAD).until( EC.title_is('PyPI – the Python Package Index · PyPI' ))
        except:
            ret = False
        return ret
        
    def searchPackage(self,searchText):       
        self.wd.find_element_by_id("search").clear()
        self.wd.find_element_by_id("search").send_keys("%s" % str(searchText).strip())
        self.wd.find_element_by_id("search").send_keys(Keys.ENTER)
        # wait for page to load, find an element on next page, order dropdown in this case. --- Removed and move to is_page_matched with wait-until function in next Page 
        # wait_element_nextPage = self.wd.find_element_by_xpath('//*[@id="order"]')
        return PyPiSearchResultPage(self.wd)

class PyPiSearchResultPage(): 
    def __init__(self, webdrive):
        self.wd = webdrive   
    
    def is_page_matched(self):
        log.info('Current page tile:' + self.wd.title)
        # return self.wd.title == 'Search results · PyPI'
        try:
            ret = WebDriverWait(self.wd, TIMEWAIT_PAGE_LOAD).until( EC.title_is('Search results · PyPI' ))
        except:
            ret = False
        return ret
        
    
    # index starts with 1
    def getSearchResultText(self,index):
        self.result_index = index
        elem_found = True
        try:
            self.elem = self.wd.find_element_by_xpath( '//*[@id="content"]/section/div/div[2]/form/section[2]/ul/li[%s]//span[1]' % self.result_index)
        except NoSuchElementException:
            log.info('Search result row not found.')
            elem_found = False
            return None   
        if elem_found == True:
            log.info('Found search result row .')
            log.info('elem text:'+ self.elem.text)
            return self.elem.text

'''
    def 
    driver.find_element_by_id("search").send_keys("selenium")
    driver.find_element_by_id("search").send_keys(Keys.ENTER)
    try: self.assertEqual("selenium", driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Add filter'])[1]/following::span[1]").text)
    except AssertionError as e: self.verificationErrors.append(str(e))
    self.assertEqual("3.141.1", driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='selenium'])[1]/following::span[1]").text)
'''        

# Check exist by xpath        
def is_element_present_by_xpath(webdriver,xpath):
    try:
        webdriver.find_element_by_xpath(xpath)
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
find_element_by_id
find_element_by_name
find_element_by_xpath  -- Recommend this
find_element_by_link_text
find_element_by_partial_link_text
find_element_by_tag_name
find_element_by_class_name
find_element_by_css_selector  -- Don't like this because it has spaces in the path
find_element   - General, can replace above methods.
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
def disable_test_locators():
    global browser
    # wd.get('https://www.seleniumhq.org/')
    browser.get('http://127.0.0.1:8000/')        
    elem_found = True
    try:
        elem = browser.find_element_by_id('loginForm')
        elem = browser.find_element_by_name('password')
        
        # Below all find the same form element
        login_form = browser.find_element_by_xpath("/html/body/form")
        login_form = browser.find_element_by_xpath("/html/body/form[1]")
        login_form = browser.find_element_by_xpath("//form[1]")
        login_form = browser.find_element_by_xpath("//form[@id='loginForm']")
        login_form = browser.find_element_by_xpath("//*[@id='loginForm']")
        login_form = browser.find_element_by_xpath("//*[@id='loginForm'][1]")
        
        # Below all find the same username element
        username_elem = browser.find_element_by_xpath("//input[@name='username']")
        username_elem = browser.find_element_by_xpath("//*[@name='username']")
        username_elem = browser.find_element_by_xpath("//*[@id='loginForm']/input[1]")
        
        # Find username input by general method find_element
        username_elem = browser.find_element(By.XPATH,"//*[@id='loginForm']/input[1]")
        username_elem = browser.find_element(By.NAME,"username")
        
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

def test_temp():
    global browser
    # wd.get('https://www.seleniumhq.org/')
    browser.get('http://pypi.org') 
    browser.find_element_by_id("search").clear()
    browser.find_element_by_id("search").send_keys("selenium")
    browser.find_element_by_id("search").send_keys(Keys.ENTER)    
    # browser.implicitly_wait(3)
    elem_found = True
    #try:
        # elem = browser.find_element_by_xpath( '//*[@id="order"]')
    try:
        ret = WebDriverWait(browser, 5).until( EC.title_is('Search results · PyPI=' ))
    except:
        ret = False
    print('element found')
    print ('return is %s' % ret )
    
    print('Finishing function')
    assert ret
        
# Test without pytest
def main():        
    setup_function()    
    test_seleniumhq_homepage()
    teardown_function()    
    
# main()    