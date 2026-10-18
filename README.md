# Automação de Processos e Organização Operacional (Robô STI)

## Sobre o Projeto

Este projeto foi desenvolvido com o objetivo de otimizar e automatizar rotinas operacionais no meu dia a dia profissional. A aplicação automatiza etapas repetitivas de extração, tratamento e organização de dados/documentos que anteriormente demandavam um tempo significativo de execução manual.

Com a implementação desta automação, foi possível:
- **Reduzir substancialmente o tempo operacional** dedicado a tarefas repetitivas.
- **Minimizar erros manuais** de conferência e classificação de arquivos.
- **Garantir maior precisão e agilidade** no fluxo de trabalho interno.

---

## Tecnologias Utilizadas

- **Python** (Lógica principal e automação)
- **Selenium & WebDriver Manager** (Navegação web e extração automatizada)
- **PyInstaller** (Compilação do projeto em um executável standalone para fácil uso no ambiente Windows)

---

## Sequência para Criar o Projeto

Siga estes passos para configurar e inicializar o projeto do zero:

1. **Crie seu ambiente virtual:**
   ```bash
   python -m venv venv
   ```

2. **Ativar o ambiente virtual:**
   ```bash
   venv\Scripts\activate
   ```

3. **Instalar as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Gerar arquivo com as dependências:**
   *(Após instalar qualquer dependência nova, execute este comando)*
   ```bash
   python -m pip freeze > requirements.txt
   ```

5. **Criar o arquivo executável:**
    ```bash
    python -m PyInstaller --onefile --hidden-import=selenium.webdriver.chrome.webdriver --hidden-import=selenium.webdriver.chrome.service --hidden-import=webdriver_manager.chrome --hidden-import=webdriver_manager.core.download_manager --hidden-import=webdriver_manager.core.driver_cache main.py; if ($?) { Move-Item -Path "dist\main.exe" -Destination ".\robô_sti.exe" -Force; Remove-Item -Path "build", "dist" -Recurse -Force; Remove-Item -Path "*.spec" -Force; Write-Host "Executável gerado e pastas limpas com sucesso!" -ForegroundColor Green }
    ```