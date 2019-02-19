import pytest
@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])
    if report.when == 'call':
        # always add url to report
        # extra.append(pytest_html.extras.url('http://www.example.com/'))
        xfail = hasattr(report, 'wasxfail')
        if (report.skipped and xfail) or (report.failed and not xfail):
            # only add additional html on failure
            # extra.append(pytest_html.extras.html('<div>Additional HTML</div>'))
            # capture screenshot on failure. Not helpful because you have to specify a image file, not to create screenshot automatically.
            # extra.append(pytest_html.extras.image('selenium_homepage.png'))
        report.extra = extra