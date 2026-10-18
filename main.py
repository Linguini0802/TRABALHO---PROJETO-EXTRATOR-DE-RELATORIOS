"""
Arquivo Principal (Orquestrador) do Robô de Extração do Portal STI.

Esse é o arquivo que você deve executar para rodar o robô e o arquivo
que você deve passar para o PyInstaller para gerar o executável (.exe).
"""

import os
import time

# Importações dos módulos locais que criamos nos passos anteriores
from config import (
    NOME_RELATORIO_FINAL, PADRAO_ARQUIVO_RELATORIO, NOVAS_COLUNAS,
    descobrir_pasta_base, carregar_configuracao, OperacaoNaoEncontrada
)
from utils import limpar_downloads_travados
from navegador import iniciar_navegador, fazer_login
from processamento import (
    processar_operacao, recuperar_estado, consolidar_e_salvar, exibir_resumo
)


def main():
    inicio = time.time()
    print('Script em andamento...\n')

    # Configuração de caminhos base
    pasta_base = descobrir_pasta_base()
    pasta_downloads = os.path.expanduser("~/Downloads")
    caminho_final = os.path.join(os.getcwd(), NOME_RELATORIO_FINAL)

    # Carrega os dados da planilha info_sti.xlsx
    operacoes, url_site, usuario, senha = carregar_configuracao(pasta_base)

    # Listas de controle por categoria de resultado
    lista_dfs = []
    operacoes_sem_veiculo = []
    operacoes_com_erro = []
    operacoes_nao_encontradas = []

    # Limpeza preventiva na pasta Downloads
    limpar_downloads_travados(pasta_downloads, PADRAO_ARQUIVO_RELATORIO)

    # Inicializa o navegador e realiza o login
    driver, wait = iniciar_navegador()
    
    try:
        fazer_login(driver, wait, url_site, usuario, senha)

        print('=== OPERAÇÕES ADICIONADAS ===\n')
        for operacao in operacoes:
            try:
                df = processar_operacao(driver, wait, operacao, pasta_downloads)
            except OperacaoNaoEncontrada:
                operacoes_nao_encontradas.append(operacao)
                print(f'  [info] A operação {operacao} não foi encontrada no portal.')
                recuperar_estado(wait)
                continue
            except Exception as e:
                # Segurança para que o erro de uma operação não derrube o robô inteiro
                operacoes_com_erro.append(operacao)
                print(f'  [ERRO] Falha inesperada na operação {operacao}: {type(e).__name__}: {e}')
                recuperar_estado(wait)
                continue

            # Validação do retorno dos dados
            if df is not None and not df.empty:
                df.insert(0, "Operação", operacao)
                df.columns = NOVAS_COLUNAS
                lista_dfs.append(df)
                print(f'A operação {operacao} foi adicionada com sucesso')
            elif df is not None and df.empty:
                operacoes_sem_veiculo.append(operacao)
                print(f'  [info] A operação {operacao} não possui veículos.')
            else:
                operacoes_com_erro.append(operacao)
                print(f'  [ERRO] Não foi possível baixar o relatório da operação {operacao} após várias tentativas.')
    
    finally:
        # Garante o fechamento do navegador mesmo se houver queda de energia/erros brutos
        driver.quit()

    # Consolida os dados no Excel e exibe o relatório no terminal
    consolidar_e_salvar(lista_dfs, caminho_final)
    exibir_resumo(operacoes_sem_veiculo, operacoes_com_erro, operacoes_nao_encontradas)

    # Cálculo do tempo de execução
    duracao = time.time() - inicio
    minutos, segundos = divmod(int(duracao), 60)
    print(f"\nAUTOMAÇÃO FINALIZADA! PODE VERIFICAR A PLANILHA '{NOME_RELATORIO_FINAL}'")
    print(f"Tempo total de execução: {minutos}m {segundos}s")
    input("\nPressione ENTER para fechar...")


if __name__ == "__main__":
    main()
