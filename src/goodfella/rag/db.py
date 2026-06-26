"""
Configuração do banco de dados vetorial embutido (ChromaDB).
"""

from pathlib import Path
import chromadb
from chromadb.config import Settings

from goodfella.core.env import GOODFELLA_DIR

def get_db_path() -> Path:
    """Retorna o caminho absoluto onde o ChromaDB persistirá os dados."""
    return Path.cwd() / GOODFELLA_DIR / "chroma_db"

def get_client() -> chromadb.PersistentClient:
    """
    Inicializa e retorna o cliente ChromaDB em modo embutido e persistente.
    """
    db_path = get_db_path()
    
    # Garante que os diretórios necessários existem antes de invocar o Chroma
    db_path.mkdir(parents=True, exist_ok=True)
    
    client = chromadb.PersistentClient(
        path=str(db_path),
        settings=Settings(
            anonymized_telemetry=False,
            is_persistent=True
        )
    )
    return client

def get_collection(client: chromadb.PersistentClient, collection_name: str = "goodfella_codebase"):
    """
    Retorna a coleção principal de vetores ou cria uma nova se não existir.
    """
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"} # Usa similaridade de cosseno, melhor para texto/código
    )
