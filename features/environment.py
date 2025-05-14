import os
import threading
import time
import subprocess
from wsgiref import simple_server

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProjecteWeb.settings')
import django
django.setup()

from django.core.management import call_command
from django.urls import reverse
from splinter.browser import Browser
from django.test.testcases import LiveServerTestCase
from django.test.runner import DiscoverRunner

def django_test_server():
    """Inicia el servidor Django per a les proves"""
    process = subprocess.Popen(
        ["python", "manage.py", "runserver", "--noreload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return process

def before_all(context):
    # Iniciar el servidor Django en un subprocés
    context.server_process = django_test_server()
    time.sleep(2)  # Donar temps al servidor per iniciar-se
    
    # Iniciar el navegador
    context.browser = Browser('chrome', headless=True)
    
    # Configurar la funció get_url
    context.base_url = "http://localhost:8000"
    context.get_url = lambda path: f"{context.base_url}{path}"
    
    # Inicialitzar la base de dades
    # call_command('flush', interactive=False, verbosity=0)

def after_all(context):
    # Tancar el navegador
    context.browser.quit()
    context.browser = None
    
    # Tancar el servidor Django
    if hasattr(context, 'server_process'):
        context.server_process.terminate()
        context.server_process.wait()
    
def before_scenario(context, scenario):
    # Opcional: Reiniciar la BD entre escenaris
    # call_command('flush', interactive=False, verbosity=0)
    pass
