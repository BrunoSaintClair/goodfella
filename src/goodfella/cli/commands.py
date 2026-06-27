"""
Módulo responsável pelos comandos utilitários da CLI.
"""

import shutil
import questionary
from rich.prompt import Prompt, Confirm

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
        ("/clear", "Limpa a tela do terminal."),
        ("/reset", "Apaga o histórico de conversação atual."),
        ("/exit ou /quit", "Encerra a aplicação.")
    ]
    
    for cmd, desc in commands:
        console.print(f"  [bold cyan]{cmd}[/bold cyan] - {desc}")
    console.print()
