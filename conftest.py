def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'integration: Mark a test as a integration test.'
    )
