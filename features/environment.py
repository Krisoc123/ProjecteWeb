from splinter.browser import Browser
from selenium.webdriver.chrome.options import Options
import os
import datetime
from pathlib import Path

def before_all(context):
    chrome_options = Options()
    # Headless mode is required in Docker
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    context.browser = Browser('chrome', options=chrome_options)
    context.browser.driver.set_page_load_timeout(60)  # Increased timeout
    context.browser.driver.implicitly_wait(15)  # Increased wait time
    
    # Create screenshots directory if it doesn't exist
    context.screenshots_dir = Path(__file__).parent / "screenshots"
    context.screenshots_dir.mkdir(exist_ok=True)

def after_all(context):
    context.browser.quit()
    context.browser = None

def before_scenario(context, scenario):
    # Reset the browser before each scenario
    context.browser.cookies.delete()
    
    # Create test books for book card tests
    # Aquest és el codi que faltava per crear els llibres de test
    if 'book_card' in scenario.feature.name.lower():
        from django.utils import timezone
        from web.models import Book

        # Comprova si els llibres ja existeixen
        if not Book.objects.filter(ISBN="1234567890").exists():
            Book.objects.create(
                ISBN="1234567890",
                title="Test Book",
                author="Test Author",
                topic="Test Topic",
                publish_date=timezone.now().date(),
                base_price=10
            )
        
        if not Book.objects.filter(ISBN="9876543210").exists():
            Book.objects.create(
                ISBN="9876543210",
                title="Another Book",
                author="Another Author",
                topic="Novel·la",
                publish_date=timezone.now().date(),
                base_price=15
            )

def after_scenario(context, scenario):
    # Log out after each scenario to ensure clean state
    context.browser.visit(context.get_url('/logout/'))
