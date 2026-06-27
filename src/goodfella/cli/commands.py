"""
Módulo responsável pelos comandos utilitários da CLI.
"""

import shutil
import questionary
from rich.prompt import Prompt, Confirm
from pathlib import Path
from typing import Tuple, Optional

from goodfella.rag.scanner import scan_workspace

from goodfella.cli.ui import console, show_spinner
from goodfella.core.config import load_config, save_config, DEFAULT_CONFIG
from goodfella.core.env import init_environment
from goodfella.rag.db import get_client, get_collection, get_db_path
from goodfella.rag.chunker import run_indexing_pipeline
from goodfella.knowledge.rules import sync_rules

def handle_setup() -> None:
    """
    Inicia o assistente de configuração para definir provedor e chaves de API.
    """
    config = load_config()
    
    console.print("\n[bold magenta]=== Configuração do Goodfella ===[/bold magenta]")
    
    valid_providers = list(DEFAULT_CONFIG["models"].keys())
    current_provider = config.get("provider", "ollama").lower()
    
    default_idx = valid_providers.index(current_provider) if current_provider in valid_providers else 0
    
    provider = questionary.select(
        "Escolha o provedor padrão:",
        choices=valid_providers,
        default=valid_providers[default_idx]
    ).ask()
    
    if not provider:
        console.print("[warning]Operação cancelada.[/warning]\n")
        return
    
    config["provider"] = provider
    
    if provider != "ollama":
        current_key = config["api_keys"].get(provider, "")
        prompt_msg = f"Digite a API Key para {provider}"
        if current_key:
            prompt_msg += " (deixe em branco para manter a atual)"
            
        key = Prompt.ask(prompt_msg, password=True, default="")
        if key.strip():
            config["api_keys"][provider] = key.strip()
    
    save_config(config)
    console.print("[success]Configuração salva com sucesso![/success]\n")

def handle_status() -> None:
    """
    Exibe o status do banco de dados, provedor e configuração atual.
    """
    config = load_config()
    provider = config.get("provider", "ollama").lower()
    has_key = bool(config["api_keys"].get(provider, ""))
    
    console.print("\n[bold magenta]=== Status do Goodfella ===[/bold magenta]")
    console.print(f"[info]Provedor Ativo:[/info] {provider}")
    
    if provider != "ollama":
        key_status = "[success]Configurada[/success]" if has_key else "[danger]Não Configurada[/danger]"
        console.print(f"[info]API Key ({provider}):[/info] {key_status}")
    
    try:
        client = get_client()
        col = get_collection(client)
        count = col.count()
        console.print(f"[info]Vetores na base local:[/info] {count}")
    except Exception as e:
        console.print(f"[danger]Erro ao acessar banco vetorial:[/danger] {e}")
    console.print()

def handle_refresh() -> None:
    """
    Força a sincronização do banco vetorial local (RAG).
    """
    console.print()
    with show_spinner("Sincronizando base de código e regras..."):
        sync_rules()
        run_indexing_pipeline()
    console.print("[success]Sincronização concluída![/success]\n")

def handle_rebuild() -> None:
    """
    Apaga completamente o banco vetorial local e força uma recriação.
    """
    console.print("\n[bold red]ATENÇÃO:[/bold red] Isso apagará fisicamente o banco vetorial do projeto.")
    console.print("Ele será reconstruído do zero, o que pode levar algum tempo.\n")
    
    if Confirm.ask("Deseja realmente prosseguir?"):
        db_path = get_db_path()
        try:
            if db_path.exists():
                shutil.rmtree(db_path, ignore_errors=True)
            console.print("[info]Banco apagado. Reconstruindo...[/info]")
            
            # Recria o diretório se necessário e roda a pipeline
            init_environment()
            with show_spinner("Reconstruindo base vetorial..."):
                sync_rules()
                run_indexing_pipeline()
            console.print("[success]Base reconstruída com sucesso![/success]\n")
        except Exception as e:
            console.print(f"[danger]Erro ao reconstruir base:[/danger] {e}\n")
    else:
        console.print("[info]Operação cancelada.[/info]\n")

def handle_help() -> None:
    """
    Exibe a lista de comandos disponíveis e suas descrições.
    """
    console.print("\n[bold magenta]=== Comandos Disponíveis ===[/bold magenta]")
    
    commands = [
        ("/help", "Exibe mensagem de ajuda com todos os comandos."),
        ("/setup", "Configura provedor (Ollama, OpenAI, Gemini) e chaves de API."),
        ("/status", "Mostra o status atual: provedor ativo, chaves e tamanho do banco vetorial."),
        ("/refresh", "Força a sincronização dos arquivos do projeto com o banco vetorial local."),
        ("/rebuild", "Apaga fisicamente o banco vetorial e reconstrói do zero (útil para corrupções)."),
        ("/review [arquivos]", "Inicia revisão de código cruzada com regras arquiteturais via RAG."),
        ("/clear", "Limpa a tela do terminal."),
        ("/reset", "Apaga o histórico de conversação atual."),
        ("/exit ou /quit", "Encerra a aplicação.")
    ]
    
    for cmd, desc in commands:
        console.print(f"  [bold cyan]{cmd}[/bold cyan] - {desc}")
    console.print()

def handle_review(cmd: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Inicia o fluxo do comando /review.
    - Se chamado sem argumentos, exibe menu interativo para escolha de arquivos.
    - Se chamado com argumentos, pega os caminhos passados.
    Lê os arquivos, busca regras no RAG usando fragmentos do código e injeta 
    isso no System Prompt retornado, junto com uma breve mensagem de usuário.
    """
    parts = cmd.split(maxsplit=1)
    files_to_review = []
    
    if len(parts) == 1:
        valid_files = scan_workspace()
        if not valid_files:
            console.print("[warning]Nenhum arquivo encontrado no projeto para revisão.[/warning]")
            return None, None
            
        choices = [str(p.relative_to(Path.cwd())) for p in valid_files]
        selected = questionary.checkbox(
            "Selecione os arquivos para review (Espaço para marcar, Enter para confirmar):",
            choices=choices
        ).ask()
        
        if not selected:
            console.print("[info]Review cancelado.[/info]\n")
            return None, None
        files_to_review = selected
    else:
        raw_files = parts[1].replace(",", " ").split()
        files_to_review = raw_files
        
    code_contents = []
    for f in files_to_review:
        f_path = Path.cwd() / f
        if f_path.exists() and f_path.is_file():
            try:
                content = f_path.read_text(encoding="utf-8")
                code_contents.append(f"--- Arquivo: {f} ---\n{content}")
            except Exception:
                console.print(f"[warning]Erro ao ler {f}[/warning]")
        else:
            console.print(f"[warning]Arquivo {f} não encontrado.[/warning]")
            
    if not code_contents:
        return None, None
        
    combined_code = "\n\n".join(code_contents)
    
    client = get_client()
    col = get_collection(client)
    
    query_text = combined_code[:1000]
    
    try:
        results = col.query(
            query_texts=[query_text],
            n_results=5,
            where={"is_rule": True}
        )
        if results and results.get("documents") and len(results["documents"]) > 0:
            rules_context = "\n\n".join(results["documents"][0])
        else:
            rules_context = ""
    except Exception as e:
        console.print(f"[warning]Aviso: Falha ao buscar regras no RAG: {e}[/warning]")
        rules_context = ""
        
    system_prompt = (
        "Você é o Goodfella, um AI Pair Programmer focado em engenharia de software pragmática.\n"
        "Realize um Code Review estrito do código do projeto atual.\n\n"
        "CÓDIGO-FONTE A SER REVISADO:\n"
        f"{combined_code}\n\n"
        "REGRAS DE ARQUITETURA E ANTI-PATTERNS (RAG):\n"
        f"{rules_context}\n\n"
        "Forneça sua análise com base estritamente nas regras listadas (se aplicável) e nas boas práticas.\n"
        "Não se desculpe, seja direto e liste sugestões práticas de código."
    )
    
    user_message = f"/review {', '.join(files_to_review)}"
    
    return user_message, system_prompt

