"""
Utilitários de interface de usuário (UI) e estilização usando a biblioteca Rich.
"""

from contextlib import contextmanager
from typing import Generator

from rich.console import Console
from rich.theme import Theme

# Define um tema base
custom_theme = Theme({
    "info": "dim white",
    "warning": "magenta",
    "danger": "bold red",
    "success": "bold green",
})

# Console global compartilhado por todo CLI
console = Console(theme=custom_theme)

@contextmanager
def show_spinner(message: str) -> Generator[None, None, None]:
    """
    Context manager que exibe um spinner animado enquanto uma operação lenta
    (ex: I/O de disco, ingestão RAG ou resposta do LLM) ocorre em background.
    
    Exemplo de uso:
        with show_spinner("Processando arquivos..."):
            do_heavy_work()
    """
    with console.status(f"[bold cyan]{message}[/bold cyan]", spinner="dots"):
        yield
