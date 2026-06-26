"""
Carregamento e vetorização de Regras e Anti-Patterns.
"""

from pathlib import Path
from typing import List, Union

from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

from goodfella.core.env import GOODFELLA_DIR
from goodfella.rag.db import get_client, get_collection

def get_rules_directories(workspace_dir: Union[Path, str] = None) -> List[Path]:
    """
    Retorna a lista de diretórios onde as regras em Markdown devem ser procuradas.
    1. Global: ~/.goodfella_config/rules
    2. Local: <workspace>/.goodfella/rules
    """
    if workspace_dir is None:
        workspace_dir = Path.cwd()
    elif isinstance(workspace_dir, str):
        workspace_dir = Path(workspace_dir)
        
    global_rules_dir = Path.home() / ".goodfella_config" / "rules"
    local_rules_dir = workspace_dir / GOODFELLA_DIR / "rules"
    
    return [global_rules_dir, local_rules_dir]

def sync_rules(workspace_dir: Union[Path, str] = None) -> int:
    """
    Lê os arquivos de regras (.md) dos diretórios globais e locais, 
    quebra-os considerando a sintaxe de Markdown e os insere no ChromaDB.
    
    Os chunks inseridos recebem a flag "is_rule": True em seus metadados, 
    o que permitirá que o motor de LLM priorize ou filtre exclusivamente
    essas diretrizes arquiteturais durante a recuperação de contexto.
    """
    if workspace_dir is None:
        workspace_dir = Path.cwd()
    elif isinstance(workspace_dir, str):
        workspace_dir = Path(workspace_dir)

    client = get_client()
    collection = get_collection(client)
    
    rules_dirs = get_rules_directories(workspace_dir)
    
    docs_to_add = []
    metadatas_to_add = []
    ids_to_add = []
    
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.MARKDOWN,
        chunk_size=1000,
        chunk_overlap=200
    )
    
    indexed_count = 0
    
    for r_dir in rules_dirs:
        if not r_dir.exists() or not r_dir.is_dir():
            continue
            
        for md_file in r_dir.glob("**/*.md"):
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                if not content.strip():
                    continue
                    
                chunks = splitter.split_text(content)
                abs_path = str(md_file.absolute())
                
                for i, chunk in enumerate(chunks):
                    chunk_id = f"RULE::{abs_path}::{i}"
                    docs_to_add.append(chunk)
                    metadatas_to_add.append({
                        "file_path": abs_path,
                        "is_rule": True,
                        "chunk_index": i
                    })
                    ids_to_add.append(chunk_id)
                    
                indexed_count += 1
            except (UnicodeDecodeError, IOError):
                pass
                
    if docs_to_add:
        collection.upsert(
            documents=docs_to_add,
            metadatas=metadatas_to_add,
            ids=ids_to_add
        )
        
    return indexed_count
