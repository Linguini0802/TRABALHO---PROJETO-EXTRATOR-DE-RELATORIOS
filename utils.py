"""
Funções utilitárias para manipulação de arquivos, monitoramento e validação de downloads.
"""

import os
import glob
import time
import pandas as pd

# Importamos as configurações necessárias do nosso arquivo config.py
from config import TIMEOUT_DOWNLOAD_SEGUNDOS, MAX_TENTATIVAS_DOWNLOAD


def get_arquivo_mais_recente(pasta, padrao):
    """Retorna o caminho do arquivo mais recente na pasta que bate com o padrão."""
    arquivos = sorted(glob.glob(os.path.join(pasta, padrao)), key=os.path.getmtime, reverse=True)
    return arquivos[0] if arquivos else None


def limpar_downloads_travados(pasta, padrao):
    """
    Remove arquivos .crdownload do padrão do relatório que ficaram travados.
    Sem isso, um arquivo travado de uma tentativa anterior bloqueia a detecção
    de todos os downloads seguintes.
    """
    for arquivo in glob.glob(os.path.join(pasta, padrao + ".crdownload")):
        try:
            os.remove(arquivo)
        except OSError:
            pass


def aguardar_download(pasta, padrao, arquivos_anteriores, timeout=TIMEOUT_DOWNLOAD_SEGUNDOS):
    """Aguarda um arquivo NOVO aparecer na pasta, ignorando os preexistentes."""
    padrao_em_andamento = padrao + ".crdownload"
    limite = time.time() + timeout
    while time.time() < limite:
        em_andamento = glob.glob(os.path.join(pasta, padrao_em_andamento))
        arquivo = get_arquivo_mais_recente(pasta, padrao)
        if arquivo and not em_andamento and arquivo not in arquivos_anteriores:
            return arquivo
        time.sleep(0.5)
    return None


def arquivo_valido(caminho):
    """
    Confere se o arquivo baixado é um Excel legível e não está vazio/corrompido.
    Retorna o DataFrame se for válido, ou None se algo deu errado no download.
    """
    try:
        if not os.path.exists(caminho) or os.path.getsize(caminho) == 0:
            return None
        return pd.read_excel(caminho, skiprows=2, header=None)
    except Exception:
        return None
