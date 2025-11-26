#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Este script automatiza a configuração inicial de um ambiente Python focado em
performance, segurança e integridade.
"""

import platform
import subprocess
import sys
from pathlib import Path
from typing import List, NoReturn

# Constantes de configuração
PYPROJECT_TOML_PATH = Path("pyproject.toml")
PRE_COMMIT_CONFIG_PATH = Path(".pre-commit-config.yaml")
GITHUB_DIR = Path(".github")
DEPENDABOT_CONFIG_PATH = GITHUB_DIR / "dependabot.yml"

# --- Funções de Utilidade ---

def _handle_error(message: str) -> NoReturn:
    """Exibe uma mensagem de erro e encerra o script."""
    print(f"❌ Erro: {message}", file=sys.stderr)
    sys.exit(1)

def _run_command(command: List[str], capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    """Executa um comando no shell e trata erros."""
    try:
        result = subprocess.run(
            command,
            check=True,
            text=True,
            encoding='utf-8',
            capture_output=capture_output,
        )
        return result
    except FileNotFoundError:
        _handle_error(f"Comando '{command[0]}' não encontrado. Verifique se ele está instalado e no PATH.")
    except subprocess.CalledProcessError as e:
        error_message = f"O comando `{' '.join(command)}` falhou com o código de saída {e.returncode}."
        if e.stderr:
            error_message += f"\nErro:\n{e.stderr}"
        _handle_error(error_message)

def _is_windows() -> bool:
    """Verifica se o sistema operacional é Windows."""
    return platform.system() == "Windows"

# --- Funções de Geração de Configuração ---

def _generate_pyproject_config() -> None:
    """Gera e escreve as configurações do Ruff e Mypy no pyproject.toml."""
    print("📝 Gerando configurações para Ruff, Mypy e Pytest no pyproject.toml...")

    try:
        pyproject_content = PYPROJECT_TOML_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        _handle_error("O arquivo pyproject.toml não foi encontrado. Execute `poetry init` primeiro.")
    except (OSError, PermissionError) as e:
        _handle_error(f"Não foi possível ler o arquivo pyproject.toml: {e}")

    config_to_add = ""

    if "[tool.ruff]" not in pyproject_content:
        config_to_add += """
# --- Configurações de Qualidade de Código ---
[tool.ruff]
line-length = 88
select = [
    "F", "E", "W", "I", "N", "D", "Q", "S", "B", "A", "C4", "T20", "SIM", "PTH",
    "TID", "ARG", "PIE", "PLC", "PLE", "PLR", "PLW", "RUF"
]
ignore = ["D203", "D212", "D213", "D416", "D417", "B905"]

[tool.ruff.mccabe]
max-complexity = 10
"""

    if "[tool.mypy]" not in pyproject_content:
        config_to_add += """
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_unimported = true
no_implicit_optional = true
check_untyped_defs = true
strict_optional = true
strict_equality = true
"""

    if "[tool.pytest.ini_options]" not in pyproject_content:
        config_to_add += """
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=."
"""

    if config_to_add:
        try:
            with PYPROJECT_TOML_PATH.open("a", encoding="utf-8") as f:
                f.write(config_to_add)
        except (OSError, PermissionError) as e:
            _handle_error(f"Não foi possível escrever no arquivo pyproject.toml: {e}")
    else:
        print("✅ Configurações de Ruff, Mypy e Pytest já existem no pyproject.toml.")


def _generate_pre_commit_config() -> None:
    """Gera e escreve o arquivo de configuração do .pre-commit-config.yaml."""
    print("📝 Gerando arquivo de configuração .pre-commit-config.yaml...")
    config_content = """
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: 'v0.4.4'
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: 'v1.10.0'
    hooks:
      - id: mypy

  - repo: https://github.com/PyCQA/bandit
    rev: '1.7.9'
    hooks:
      - id: bandit
        args: ["-r", "."]

  - repo: https://github.com/pycqa/safety
    rev: '3.2.3'
    hooks:
      - id: safety
        args: ["--full-report"]

  - repo: https://github.com/semgrep/pre-commit
    rev: 'v1.69.1'
    hooks:
      - id: semgrep
        args: ['--config=auto']
"""
    try:
        PRE_COMMIT_CONFIG_PATH.write_text(config_content, encoding="utf-8")
    except (OSError, PermissionError) as e:
        _handle_error(f"Não foi possível criar o arquivo .pre-commit-config.yaml: {e}")

def _generate_dependabot_config() -> None:
    """Gera o arquivo de configuração do Dependabot."""
    print("📝 Gerando arquivo de configuração .github/dependabot.yml...")
    try:
        GITHUB_DIR.mkdir(exist_ok=True)
    except (FileExistsError, PermissionError) as e:
        _handle_error(f"Não foi possível criar o diretório .github: {e}")

    config_content = """version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "daily"
    groups:
      dev-dependencies:
        patterns:
          - "ruff"
          - "mypy"
          - "bandit"
          - "safety"
          - "pytest*"
          - "pre-commit"
          - "semgrep"
          - "py-spy"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "daily"
"""
    try:
        DEPENDABOT_CONFIG_PATH.write_text(config_content, encoding="utf-8")
    except (OSError, PermissionError) as e:
        _handle_error(f"Não foi possível criar o arquivo .github/dependabot.yml: {e}")

# --- Funções de Orquestração ---

def _initialize_poetry_project() -> None:
    """Inicializa um novo projeto Poetry."""
    if PYPROJECT_TOML_PATH.exists():
        print("✅ Projeto Poetry já inicializado.")
        return

    print("🛠️  Inicializando projeto Poetry...")
    _run_command(["poetry", "init", "-n"])


def _add_dependencies() -> None:
    """Adiciona as dependências de produção e desenvolvimento ao projeto."""
    print("📦 Adicionando dependências de produção...")
    prod_deps = ["pydantic>=2.0", "orjson"]
    if not _is_windows():
        prod_deps.append("uvloop")

    _run_command(["poetry", "add"] + prod_deps)

    print("🔧 Adicionando dependências de desenvolvimento...")
    dev_deps = [
        "ruff", "mypy", "bandit", "safety", "pre-commit",
        "pytest", "pytest-cov", "py-spy", "semgrep"
    ]
    _run_command(["poetry", "add", "--group", "dev"] + dev_deps)


def _setup_pre_commit_hooks() -> None:
    """Instala e configura os hooks de pre-commit."""
    print("⚙️  Instalando hooks de pre-commit...")
    _run_command(["poetry", "run", "pre-commit", "install"])


def main() -> None:
    """Função principal para orquestrar a configuração do ambiente."""
    print("🚀 Iniciando a configuração do ambiente Python de alta performance...")

    _initialize_poetry_project()
    _add_dependencies()
    _generate_pyproject_config()
    _generate_pre_commit_config()
    _generate_dependabot_config()
    _setup_pre_commit_hooks()

    print("\n✅ Ambiente configurado com sucesso!")
    print("Execute `poetry shell` para ativar o ambiente virtual.")
    print("💡 Dica: execute `poetry config virtualenvs.in-project true` para criar o .venv dentro do projeto.")


if __name__ == "__main__":
    main()
