"""
Scanner Inteligente de arquivos para indexação (RAG).
"""

import os
import fnmatch
from pathlib import Path
from typing import List, Union

from goodfella.core.constants import IGNORED_DIRS, SUPPORTED_EXTENSIONS

def load_gitignore_patterns(workspace_dir: Path) -> List[str]:
    """
    Lê o .gitignore do repositório ativo e retorna os padrões de exclusão.
    """
    gitignore_path = workspace_dir / ".gitignore"
    patterns = []
    
    if gitignore_path.exists():
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
                    
    return patterns

def is_ignored(path: Path, workspace_dir: Path, gitignore_patterns: List[str]) -> bool:
    """
    Decide se o caminho (arquivo ou pasta) deve ser ignorado pela indexação.
    Verifica a lista de constantes globais (IGNORED_DIRS) e o .gitignore ativo.
    """
    rel_path = path.relative_to(workspace_dir)
    
    # 1. Bloqueia imediatamente diretórios críticos da constante (ex: .git, node_modules)
    for part in rel_path.parts:
        if part in IGNORED_DIRS:
            return True
            
    # 2. Se for arquivo, checar se a extensão é suportada.
    if path.is_file() and path.suffix not in SUPPORTED_EXTENSIONS:
        return True
        
    # 3. Faz o match contra as regras do .gitignore
    rel_path_str = str(rel_path)
    
    for pattern in gitignore_patterns:
        match_pattern = pattern
        
        if pattern.startswith("/"):
            match_pattern = pattern[1:]
        else:
            if not pattern.startswith("*"):
                match_pattern = f"*{pattern}*"
                
        if match_pattern.endswith("/"):
            match_pattern = match_pattern[:-1]
            
        if fnmatch.fnmatch(rel_path_str, match_pattern):
            return True
            
    return False

def scan_workspace(workspace_dir: Union[Path, str] = None) -> List[Path]:
    """
    Percorre a árvore de diretórios e retorna uma lista de arquivos 
    válidos para a ingestão.
    """
    if workspace_dir is None:
        workspace_dir = Path.cwd()
    elif isinstance(workspace_dir, str):
        workspace_dir = Path(workspace_dir)
        
    gitignore_patterns = load_gitignore_patterns(workspace_dir)
    valid_files = []
    
    for root, dirs, files in os.walk(workspace_dir):
        root_path = Path(root)
        
        # Filtra a lista de pastas. Se ela for ignorada, o os.walk não vai entrar nela.
        dirs[:] = [
            d for d in dirs 
            if not is_ignored(root_path / d, workspace_dir, gitignore_patterns)
        ]
        
        # Verifica e adiciona os arquivos válidos
        for file in files:
            file_path = root_path / file
            if not is_ignored(file_path, workspace_dir, gitignore_patterns):
                valid_files.append(file_path)
                
    return valid_files
