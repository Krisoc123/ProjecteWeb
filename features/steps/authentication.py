from behave import *

use_step_matcher("parse")

@given('Exists a user "{username}" with password "{password}"')
def step_impl(context, username, password):
    from django.contrib.auth.models import User
    User.objects.create_user(username=username, email=f'{username}@example.com', password=password)

@given('I login as user "{username}" with password "{password}"')
def step_impl(context, username, password):
    context.browser.visit(context.get_url('/login/'))
    context.browser.fill('username', username)
    context.browser.fill('password', password)
    # Scroll to the button first to make sure it's clickable
    button = context.browser.find_by_css('button[type="submit"]').first
    button.scroll_to()
    button.click()
    # Wait a moment for the redirect to complete
    import time
    time.sleep(1)

@given('I\'m not logged in')
def step_impl(context):
    context.browser.visit(context.get_url('/logout/'))
    # Check for any indication of being logged out, such as a login link
    assert context.browser.is_element_present_by_css('a[href*="login"]')

@then('Server responds with page containing "{message}"')
def step_impl(context, message):
    assert context.browser.is_text_present(message)

@then('There is "{link_text}" link available')
def step_impl(context, link_text):
    assert context.browser.is_element_present_by_xpath('//a[text()="'+link_text+'"]')

@then('There is no "{link_text}" link available')
def step_impl(context, link_text):
    assert context.browser.is_element_not_present_by_xpath('//a[text()="'+link_text+'"]')

@then("I'm redirected to the login form")
def step_impl(context):
    # Wait a moment for the redirect to complete
    import time
    time.sleep(2)  # Esperar más tiempo para que la redirección se complete
    
    # Based on logs, we found that checking the URL is the most reliable method
    print(f"[LOG] Redirect: URL actual: {context.browser.url}")
    
    # Verificar si estamos en la página de login
    is_login_page = False
    
    # Método 1: Verificar por URL (this method works consistently based on logs)
    if "login" in context.browser.url:
        print("[LOG] Redirect: Detectada página de login por URL")
        is_login_page = True
    else:
        # Método 2: Verificar por la presencia del formulario de login (fallback)
        try:
            if context.browser.is_element_present_by_id('id_username') and context.browser.is_element_present_by_id('id_password'):
                print("[LOG] Redirect: Detectada página de login por elementos del formulario")
                is_login_page = True
        except Exception:
            pass
    
    assert is_login_page, f"No se encontró la página de login. URL actual: {context.browser.url}"
