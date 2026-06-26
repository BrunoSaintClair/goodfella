"""
Gerenciamento de diretório e ambiente do projeto Goodfella.
"""

from pathlib import Path

GOODFELLA_DIR = ".goodfella"

def init_environment() -> None:
    """
    Inicializa o ambiente do Goodfella gerando a pasta oculta .goodfella/
    no diretório de execução atual e injetando a regra .goodfella/ no .gitignore
    do projeto para evitar commits acidentais do banco.
    """
    cwd = Path.cwd()
    goodfella_path = cwd / GOODFELLA_DIR
    
    goodfella_path.mkdir(parents=True, exist_ok=True)
    
    gitignore_path = cwd / ".gitignore"
    
    if gitignore_path.exists():
        with open(gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        lines = [line.strip() for line in content.splitlines()]
        if GOODFELLA_DIR not in lines and f"{GOODFELLA_DIR}/" not in lines:
            with open(gitignore_path, "a", encoding="utf-8") as f:
                if content and not content.endswith("\n"):
                    f.write("\n")
                f.write(f"\n# Goodfella\n{GOODFELLA_DIR}/\n")
    else:
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write(f"# Goodfella\n{GOODFELLA_DIR}/\n")