"""
Gerenciamento do ciclo de vida do navegador (abertura, login e navegação base).
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Importamos os locators e tempos configurados no arquivo config.py
from config import (
    TIMEOUT_PADRAO_SEGUNDOS,
    LOCATOR_CAMPO_USUARIO,
    LOCATOR_CAMPO_SENHA,
    LOCATOR_BOTAO_ENTRAR,
    LOCATOR_LINK_RELATORIOS
)


def iniciar_navegador():
    """Abre o Chrome controlado pelo Selenium."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, TIMEOUT_PADRAO_SEGUNDOS)
    return driver, wait


def fazer_login(driver, wait, url_site, usuario, senha):
    """Acessa o portal e realiza o login."""
    driver.get(url_site)
    wait.until(EC.visibility_of_element_located(LOCATOR_CAMPO_USUARIO)).send_keys(usuario)
    wait.until(EC.visibility_of_element_located(LOCATOR_CAMPO_SENHA)).send_keys(senha)
    wait.until(EC.element_to_be_clickable(LOCATOR_BOTAO_ENTRAR)).click()
    wait.until(EC.element_to_be_clickable(LOCATOR_LINK_RELATORIOS)).click()
