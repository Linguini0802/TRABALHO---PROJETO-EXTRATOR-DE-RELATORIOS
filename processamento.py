"""
Lógica de processamento das operações, cliques, downloads e consolidação de dados.
"""

import os
import glob
import time
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

# Importações dos nossos módulos locais
from config import (
    TIMEOUT_BUSCA_OPERACAO_SEGUNDOS, MAX_TENTATIVAS_DOWNLOAD, PADRAO_ARQUIVO_RELATORIO,
    NOVAS_COLUNAS, LOCATOR_SELECT_EMPRESA, LOCATOR_CAMPO_BUSCA_EMPRESA,
    LOCATOR_SELECT2_OPCAO, LOCATOR_SELECT2_SEM_RESULTADO, LOCATOR_LINK_RELATORIOS,
    LOCATOR_BOTAO_VISUALIZAR, LOCATOR_BOTAO_EXPORTAR, OperacaoNaoEncontrada
)
from utils import limpar_downloads_travados, aguardar_download, arquivo_valido


def baixar_com_retentativa(operacao, wait, locator_botao, pasta, padrao, max_tentativas=MAX_TENTATIVAS_DOWNLOAD):
    """
    Clica no botão de exportar e aguarda o download. Se o arquivo falhar,
    tenta clicar novamente no botão do site restabelecendo o elemento do DOM.
    """
    for tentativa in range(1, max_tentativas + 1):
        limpar_downloads_travados(pasta, padrao)
        try:
            botao_baixar = wait.until(EC.element_to_be_clickable(locator_botao))
            arquivos_antes = set(glob.glob(os.path.join(pasta, padrao)))
            botao_baixar.click()
        except (StaleElementReferenceException, TimeoutException) as erro:
            print(f"  [aviso] Botão de download indisponível -> {operacao} "
                  f"(tentativa {tentativa}/{max_tentativas}): {type(erro).__name__}")
            time.sleep(2)
            continue

        alvo = aguardar_download(pasta, padrao, arquivos_antes)
        if alvo:
            df = arquivo_valido(alvo)
            if df is not None:
                return df, alvo
            try:
                os.remove(alvo)
            except OSError:
                pass

        print(f"  [aviso] Falha no download -> {operacao} (tentativa {tentativa}/{max_tentativas}). "
              f"Tentando novamente...")
        time.sleep(2)

    return None, None


def selecionar_operacao(driver, wait, operacao):
    """Seleciona a operação no combobox (Select2) da tela de relatórios."""
    wait.until(EC.element_to_be_clickable(LOCATOR_SELECT_EMPRESA)).click()
    campo = wait.until(EC.visibility_of_element_located(LOCATOR_CAMPO_BUSCA_EMPRESA))
    campo.send_keys(operacao)

    busca_curta = WebDriverWait(driver, TIMEOUT_BUSCA_OPERACAO_SEGUNDOS)
    try:
        busca_curta.until(
            lambda d: d.find_elements(*LOCATOR_SELECT2_OPCAO) or d.find_elements(*LOCATOR_SELECT2_SEM_RESULTADO)
        )
    except TimeoutException:
        pass

    if driver.find_elements(*LOCATOR_SELECT2_SEM_RESULTADO) and not driver.find_elements(*LOCATOR_SELECT2_OPCAO):
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        raise OperacaoNaoEncontrada(f"Nenhum resultado no portal para a operação '{operacao}'")

    ActionChains(driver).send_keys(Keys.TAB).perform()
    time.sleep(1)


def recuperar_estado(wait):
    """Tenta voltar à página de relatórios para o próximo loop iniciar limpo."""
    try:
        wait.until(EC.element_to_be_clickable(LOCATOR_LINK_RELATORIOS)).click()
    except Exception:
        pass


def processar_operacao(driver, wait, operacao, pasta_downloads):
    """Processa uma única operação executando seleção, visualização e extração."""
    selecionar_operacao(driver, wait, operacao)

    wait.until(EC.element_to_be_clickable(LOCATOR_BOTAO_VISUALIZAR)).click()
    wait.until(EC.element_to_be_clickable(LOCATOR_BOTAO_EXPORTAR))
    time.sleep(3)

    df, alvo = baixar_com_retentativa(operacao, wait, LOCATOR_BOTAO_EXPORTAR, pasta_downloads, PADRAO_ARQUIVO_RELATORIO)

    if alvo:
        try:
            os.remove(alvo)
        except OSError:
            pass

    time.sleep(1)
    wait.until(EC.element_to_be_clickable(LOCATOR_LINK_RELATORIOS)).click()

    return df


def limpar_identificacao(valor):
    """Remove '-' e tudo após se houver 7+ caracteres antes dele."""
    texto = str(valor)
    if "-" in texto:
        partes = texto.split("-", 1)
        if len(partes[0]) >= 7:
            return partes[0]
    return valor


def consolidar_e_salvar(lista_dfs, caminho_final):
    """Junta os DataFrames das operações, limpa colunas e gera a planilha final."""
    if not lista_dfs:
        return

    try:
        df_final = pd.concat(lista_dfs, ignore_index=True)

        dt = pd.to_datetime(df_final["Data"], dayfirst=True, errors='coerce')
        df_final["Data"] = dt.dt.strftime('%d/%m/%Y')
        if "Hora" in df_final.columns:
            df_final = df_final.drop(columns=["Hora"])
        df_final.insert(3, "Hora", dt.dt.strftime('%H:%M:%S'))

        df_final["Identificação"] = df_final["Identificação"].apply(limpar_identificacao)

        df_final.to_excel(caminho_final, index=False)
    except Exception as e:
        print(f"\n[ERRO] Falha ao consolidar/salvar o relatório final: {e}")


def exibir_resumo(operacoes_sem_veiculo, operacoes_com_erro, operacoes_nao_encontradas):
    """Gera o relatório descritivo final no terminal."""
    if operacoes_sem_veiculo:
        print(f"\n=== OPERAÇÕES SEM VEÍCULOS ({len(operacoes_sem_veiculo)}) ===")
        for op in operacoes_sem_veiculo:
            print(f"  - {op}")

    if operacoes_nao_encontradas:
        print(f"\n=== OPERAÇÕES NÃO ENCONTRADAS NO PORTAL ({len(operacoes_nao_encontradas)}) ===")
        for op in operacoes_nao_encontradas:
            print(f"  - {op}")

    if operacoes_com_erro:
        print(f"\n=== OPERAÇÕES COM ERRO DE DOWNLOAD ({len(operacoes_com_erro)}) ===")
        for op in operacoes_com_erro:
            print(f"  - {op}")
