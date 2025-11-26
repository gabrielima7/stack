#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Este script automatiza a configuração inicial de um ambiente Python focado em
performance, segurança e integridade.
"""

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, NoReturn

# Constantes de configuração
PYPROJECT_TOML_PATH = Path("pyproject.toml")
PRE_COMMIT_CONFIG_PATH = Path(".pre-commit-config.yaml")
GITHUB_DIR = Path(".github")
DEPENDABOT_CONFIG_PATH = GITHUB_DIR / "dependabot.yml"
SECURITY_MD_PATH = Path("SECURITY.md")


# --- Funções de Utilidade ---

def _log(message: str, args: argparse.Namespace, is_verbose: bool = False) -> None:
    """Função de log centralizada que respeita os modos dry-run e verbose."""
    if is_verbose and not args.verbose:
        return

    prefix = "[DRY-RUN] " if args.dry_run else ""
    print(f"{prefix}{message}")

def _handle_error(message: str) -> NoReturn:
    """Exibe uma mensagem de erro e encerra o script."""
    print(f"❌ Erro: {message}", file=sys.stderr)
    sys.exit(1)

def _run_command(
    command: List[str], args: argparse.Namespace, capture_output: bool = False
) -> subprocess.CompletedProcess[str]:
    """Executa um comando no shell, tratando erros e modo dry-run."""
    _log(f"Executando comando: `{' '.join(command)}`", args, is_verbose=True)
    if args.dry_run:
        return subprocess.CompletedProcess(command, 0, "", "")

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
        # A verificação de Poetry é tratada separadamente, então este é um erro inesperado.
        _handle_error(f"Comando '{command[0]}' não encontrado. Verifique se ele está instalado e no PATH.")
    except subprocess.CalledProcessError as e:
        error_message = f"O comando `{' '.join(command)}` falhou com o código de saída {e.returncode}."
        if e.stderr and not capture_output:
            error_message += f"\nErro:\n{e.stderr}"
        _handle_error(error_message)

def _is_windows() -> bool:
    """Verifica se o sistema operacional é Windows."""
    return platform.system() == "Windows"

def _safe_write(path: Path, content: str, args: argparse.Namespace) -> None:
    """Escreve conteúdo em um arquivo, com backup e modo dry-run."""
    _log(f"Escrevendo no arquivo: {path}", args, is_verbose=True)
    if args.dry_run:
        return

    if path.exists() and not args.force:
        backup_path = path.with_suffix(f"{path.suffix}.bak")
        try:
            path.rename(backup_path)
            _log(f"⚠️  Backup criado: {backup_path.name}", args)
        except (OSError, PermissionError) as e:
            _handle_error(f"Não foi possível criar o backup do arquivo {path.name}: {e}")

    try:
        path.write_text(content, encoding="utf-8")
    except (OSError, PermissionError) as e:
        _handle_error(f"Não foi possível escrever no arquivo {path.name}: {e}")

# --- Funções de Geração de Configuração ---

def _generate_pyproject_config(args: argparse.Namespace) -> None:
    """Gera e escreve as configurações do Ruff e Mypy no pyproject.toml."""
    _log("📝 Gerando configurações para Ruff, Mypy e Pytest no pyproject.toml...", args)

    try:
        pyproject_content = PYPROJECT_TOML_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        # Se o pyproject.toml não existe, significa que o `poetry init` ainda não rodou.
        pyproject_content = ""

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

    if not args.dry_run and config_to_add:
        try:
            with PYPROJECT_TOML_PATH.open("a", encoding="utf-8") as f:
                f.write(config_to_add)
        except (OSError, PermissionError) as e:
            _handle_error(f"Não foi possível escrever no arquivo pyproject.toml: {e}")
    elif args.dry_run and config_to_add:
        _log("Adicionaria configurações de ferramentas ao pyproject.toml", args, is_verbose=True)
    elif not config_to_add:
        _log("✅ Configurações de Ruff, Mypy e Pytest já existem no pyproject.toml.", args)

def _generate_pre_commit_config(args: argparse.Namespace) -> None:
    """Gera e escreve o arquivo de configuração do .pre-commit-config.yaml."""
    _log("📝 Gerando arquivo de configuração .pre-commit-config.yaml...", args)
    config_content = """repos:
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
    _safe_write(PRE_COMMIT_CONFIG_PATH, config_content, args)

def _generate_dependabot_config(args: argparse.Namespace) -> None:
    """Gera o arquivo de configuração do Dependabot."""
    _log("📝 Gerando arquivo de configuração .github/dependabot.yml...", args)
    if not args.dry_run:
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
    _safe_write(DEPENDABOT_CONFIG_PATH, config_content, args)

def _generate_security_policy(args: argparse.Namespace) -> None:
    """Gera o arquivo SECURITY.md com uma política de segurança moderna."""
    _log("📝 Gerando política de segurança em SECURITY.md...", args)
    content = """# Security Policy

## Supported Versions
Nós priorizamos correções de segurança na versão mais recente (Rolling Release).

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| Older   | :x:                |

## Reporting a Vulnerability
Se encontrar uma falha, por favor reporte via aba [Security](../../security) ou email.
"""
    _safe_write(SECURITY_MD_PATH, content, args)

# --- Funções de Orquestração ---

def _check_poetry_installation(args: argparse.Namespace) -> None:
    """Verifica se o Poetry está instalado de forma inteligente."""
    _log("🔎 Verificando se o Poetry está instalado...", args)
    if shutil.which("poetry"):
        _log("✅ Poetry encontrado.", args)
        return

    # Se Poetry não foi encontrado, cria uma mensagem de erro mais útil
    if shutil.which("pipx"):
        suggestion = "Tente instalar com: `pipx install poetry`"
    else:
        suggestion = "Consulte a documentação oficial: https://python-poetry.org/docs/#installation"

    _handle_error(f"Poetry não encontrado. {suggestion}")

def _initialize_poetry_project(args: argparse.Namespace) -> None:
    """Inicializa um novo projeto Poetry."""
    if PYPROJECT_TOML_PATH.exists():
        _log("✅ Projeto Poetry já inicializado.", args)
        return
    _log("🛠️  Inicializando projeto Poetry...", args)
    _run_command(["poetry", "init", "-n"], args)

def _add_dependencies(args: argparse.Namespace) -> None:
    """Adiciona as dependências de produção e desenvolvimento ao projeto."""
    _log("📦 Adicionando dependências de produção...", args)
    prod_deps = ["pydantic>=2.0", "orjson"]
    if not _is_windows():
        prod_deps.append("uvloop")
    _run_command(["poetry", "add"] + prod_deps, args)

    _log("🔧 Adicionando dependências de desenvolvimento...", args)
    dev_deps = [
        "ruff", "mypy", "bandit", "safety", "pre-commit",
        "pytest", "pytest-cov", "py-spy", "semgrep"
    ]
    _run_command(["poetry", "add", "--group", "dev"] + dev_deps, args)

def _setup_pre_commit_hooks(args: argparse.Namespace) -> None:
    """Instala e configura os hooks de pre-commit."""
    _log("⚙️  Instalando hooks de pre-commit...", args)
    _run_command(["poetry", "run", "pre-commit", "install"], args)

def _setup_cli() -> argparse.Namespace:
    """Configura a interface de linha de comando."""
    parser = argparse.ArgumentParser(description="Automatiza a configuração de um ambiente Python de alta performance.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula a execução sem fazer alterações reais no sistema de arquivos.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Exibe logs detalhados sobre cada etapa do processo.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Força a sobrescrita de arquivos de configuração sem criar backups.",
    )
    return parser.parse_args()

def main() -> None:
    """Função principal para orquestrar a configuração do ambiente."""
    args = _setup_cli()
    _check_poetry_installation(args)
    _log("\n🚀 Iniciando a configuração do ambiente Python de alta performance...", args)
    _initialize_poetry_project(args)
    _add_dependencies(args)
    _generate_pyproject_config(args)
    _generate_pre_commit_config(args)
    _generate_dependabot_config(args)
    _generate_security_policy(args)
    _setup_pre_commit_hooks(args)
    _log("\n✅ Ambiente configurado com sucesso!", args)
    _log("Execute `poetry shell` para ativar o ambiente virtual.", args)
    _log("💡 Dica: execute `poetry config virtualenvs.in-project true` para criar o .venv dentro do projeto.", args)
    _log("\n🔒 Lembre-se de commitar o arquivo `poetry.lock` para garantir builds reprodutíveis.", args)

if __name__ == "__main__":
    main()
