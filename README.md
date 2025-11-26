# 🐍 Python Stack: Performance, Security & Integrity Bootstrapper

Este projeto fornece um script "Zero-to-Hero" que configura um ambiente de desenvolvimento Python completo em segundos. Ele automatiza a instalação e configuração de um conjunto de ferramentas de alta performance, segurança e qualidade, permitindo que você foque apenas em codificar.

## ✨ A Stack 

O script `stack.py` instala e configura um ecossistema de ferramentas cuidadosamente selecionadas para garantir a máxima eficiência e robustez do seu projeto.

| Categoria             | Ferramenta                                | Propósito                                                                      |
| --------------------- | ----------------------------------------- | ------------------------------------------------------------------------------ |
| 🚀 **Runtime**        | `Pydantic V2`                             | Validação de dados de alta performance, parsing e serialização com tipagem.    |
|                       | `Orjson`                                  | A biblioteca de serialização JSON mais rápida para Python.                     |
|                       | `Uvloop`                                  | Implementação ultra-rápida do event loop do `asyncio` (apenas para Linux/macOS). |
| 🛡️ **Qualidade & Seg.** | `Ruff`                                    | O linter e formatador mais rápido para Python, escrito em Rust.                |
|                       | `Mypy`                                    | Checagem de tipagem estática para um código mais limpo e sem bugs.             |
|                       | `Bandit`                                  | Análise Estática de Segurança (SAST) para encontrar vulnerabilidades comuns.   |
|                       | `Safety`                                  | Análise de Composição de Software (SCA) para verificar dependências inseguras. |
|                       | `Semgrep`                                 | Ferramenta de análise estática moderna para encontrar bugs e aplicar padrões.  |
|                       | `Pytest` + `pytest-cov`                   | Framework de testes poderoso com medição de cobertura de código.               |
| 🏗️ **Infraestrutura**  | `Poetry`                                  | Gestão de dependências e ambientes virtuais de forma declarativa e robusta.    |
|                       | `Pre-commit`                              | Framework para gerenciar e manter ganchos Git de pré-commit.                   |
|                       | `Dependabot`                              | Automação para manter as dependências sempre atualizadas e seguras.            |

## 🚀 Quick Start

### Pré-requisitos

- **Python 3.10+**
- **Poetry**: Recomenda-se a instalação via `pipx` para isolamento (`pipx install poetry`). O script verifica automaticamente se ele está disponível.

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/gabrielima7/stack.git
    cd stack
    ```

2.  **Execute o script:**
    O script irá configurar o Poetry, instalar todas as dependências e gerar os arquivos de configuração.
    ```bash
    python3 stack.py
    ```

3.  **Ative o ambiente virtual:**
    ```bash
    poetry shell
    ```

Pronto! Seu ambiente está configurado e pronto para uso.

## CLI e Opções Avançadas

O script possui uma interface de linha de comando para dar a você controle total sobre a execução:

-   `--dry-run`: Simula a execução sem alterações.
-   `--force`: Sobrescreve arquivos de configuração existentes sem criar backup.
-   `--verbose`: Exibe logs detalhados.

## Desenvolvimento e Testes

O projeto inclui uma suíte de testes própria (`tests/`) e um pipeline de CI que valida o script a cada commit.

## 🤖 Automação Inteligente

O `stack.py` foi projetado para ser o mais inteligente e autônomo possível:

-   **Detecção de Sistema Operacional:** O script verifica automaticamente o seu SO e instala o `uvloop` apenas em ambientes Linux e macOS, onde é compatível.
-   **Geração Automática de Configuração:** Todos os arquivos de configuração são gerados e pré-configurados com padrões rigorosos:
    -   `pyproject.toml` (com configurações para Ruff, Mypy e Pytest)
    -   `.pre-commit-config.yaml` (com hooks para Ruff, Mypy, Bandit, Safety e Semgrep)
    -   `.github/dependabot.yml` (com automação de atualização diária para `pip` e `GitHub Actions`)
    -   `SECURITY.md` (com uma política de segurança padrão)
-   **Idempotente e Seguro:** O script pode ser executado várias vezes. Por padrão, ele cria backups (`.bak`) de arquivos existentes antes de sobrescrevê-los para evitar perda de dados.
