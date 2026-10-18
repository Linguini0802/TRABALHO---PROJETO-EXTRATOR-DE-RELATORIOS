"""
Configurações, locators e gerenciamento de arquivos de entrada/saída.
"""

import os
import sys
import pandas as pd
from selenium.webdriver.common.by import By

# ==============================================================================
# CONSTANTES E PADRÕES
# ==============================================================================
NOVAS_COLUNAS = [
    "Operação", "Identificação", "Data", "Evento", "Localização",
    "Latitude", "Longitude", "Velocidade", "Operador", "Matrícula",
    "Rota", "Hodômetro", "Voltagem",
]

NOME_RELATORIO_FINAL = "relatorio_sti.xlsx"
NOME_ARQUIVO_INFO = "info_sti.xlsx"
PADRAO_ARQUIVO_RELATORIO = "Ultimas Posicoes*.xlsx"

TIMEOUT_PADRAO_SEGUNDOS = 30
TIMEOUT_DOWNLOAD_SEGUNDOS = 30
MAX_TENTATIVAS_DOWNLOAD = 3
TIMEOUT_BUSCA_OPERACAO_SEGUNDOS = 5

# ==============================================================================
# LOCATORS ( MAPEAMENTO DE ELEMENTOS WEB )
# ==============================================================================
LOCATOR_CAMPO_USUARIO = (By.XPATH, "//input[@id='usuario']")
LOCATOR_CAMPO_SENHA = (By.XPATH, "//input[@id='senha']")
LOCATOR_BOTAO_ENTRAR = (By.XPATH, "//button[@id='btnEntrar']")
LOCATOR_LINK_RELATORIOS = (By.XPATH, "//a[@href='/Portal/Relatorios']")
LOCATOR_SELECT_EMPRESA = (By.XPATH, "//span[@id='select2-selectEmpresa-container']")
LOCATOR_CAMPO_BUSCA_EMPRESA = (By.XPATH, "//input[@class='select2-search__field']")
LOCATOR_BOTAO_VISUALIZAR = (By.XPATH, "//button[@id='btnVisualizar']")
LOCATOR_BOTAO_EXPORTAR = (By.XPATH, "//button[@class='dt-button buttons-excel buttons-html5 botao-export botao-xls']")
LOCATOR_SELECT2_SEM_RESULTADO = (By.XPATH, "//li[contains(@class, 'select2-results__message')]")
LOCATOR_SELECT2_OPCAO = (By.XPATH, "//li[contains(@class, 'select2-results__option') and not(contains(@class, 'select2-results__message'))]")

# ==============================================================================
# EXCEÇÕES PERSONALIZADAS
# ==============================================================================
class OperacaoNaoEncontrada(Exception):
    """Levantada quando o portal não retorna nenhum resultado para a operação buscada."""
    pass

# ==============================================================================
# FUNÇÕES DE INFRAESTRUTURA DE CONFIGURAÇÃO
# ==============================================================================
def descobrir_pasta_base():
    """Define a pasta base do programa, compatível com execução via .py ou .exe."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def carregar_configuracao(pasta_base):
    """Lê operações e credenciais do arquivo info_sti.xlsx. Encerra o programa em caso de erro."""
    try:
        caminho_info = os.path.join(pasta_base, NOME_ARQUIVO_INFO)
        operacoes = pd.read_excel(caminho_info, sheet_name="PUXAR OPERAÇÕES").iloc[:, 0].dropna().tolist()
        df_login = pd.read_excel(caminho_info, sheet_name="SITES E LOGINS")
        url_site = df_login.iloc[0, 0]
        usuario = df_login.iloc[0, 1]
        senha = df_login.iloc[0, 2]
        return operacoes, url_site, usuario, senha
    except Exception as e:
        print(f"\n[ERRO] Não foi possível ler '{NOME_ARQUIVO_INFO}': {e}\n"
              f"Verifique se está na mesma pasta do programa.")
        input("\nPressione ENTER para fechar...")
        sys.exit()
