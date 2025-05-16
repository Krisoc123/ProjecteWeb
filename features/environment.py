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

def after_step(context, step):
    # Take a screenshot if step fails
    if step.status == "failed":
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}_{step.name}.png"
        filepath = context.screenshots_dir / filename
        context.browser.screenshot(str(filepath))
        print(f"Screenshot saved to {filepath}")

def after_scenario(context, scenario):
    # Log out after each scenario to ensure clean state
    context.browser.visit(context.get_url('/logout/'))
