"""
Settings for behave-django and project-specific configurations.
"""

from django.test.runner import DiscoverRunner

# Fixed base URL for tests
TEST_SERVER_URL = 'http://localhost:8000'

# Fixture data to load for all tests
BEHAVE_FIXTURES = ['web_data_backup.json']

# Always reuse the existing test database (use this with caution as it may cause data leakage between test runs)
# BEHAVE_REUSE_DB = True

def before_tests(context):
    context.test_runner = DiscoverRunner(interactive=False)
    context.test_runner.setup_test_environment()
    context.old_db_config = context.test_runner.setup_databases()


def after_tests(context):
    context.test_runner.teardown_databases(context.old_db_config)
    context.test_runner.teardown_test_environment()


def before_all(context):
    before_tests(context)


def after_all(context):
    after_tests(context)
