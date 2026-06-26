"""
Gerenciamento de configuração global do projeto Goodfella.
"""

import json
from pathlib import Path
from typing import Any, Dict

CONFIG_FILE_NAME = ".goodfella_config"

DEFAULT_CONFIG = {
    "provider": "Ollama",
    "api_keys": {
        "openai": "",
        "gemini": "",
        "anthropic": "",
        "deepseek": ""
    }
}

def get_config_path() -> Path:
    """
    Retorna o caminho absoluto do arquivo de configuração global.
    """
    return Path.home() / CONFIG_FILE_NAME

def load_config() -> Dict[str, Any]:
    """
    Carrega as configurações globais do arquivo ~/.goodfella_config.
    Se o arquivo não existir ou for inválido, retorna o fallback (Ollama).
    """
    config_path = get_config_path()
    
    if not config_path.exists():
        return DEFAULT_CONFIG.copy()
        
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
            
            # Merge simples para garantir chaves padrão
            merged_config = DEFAULT_CONFIG.copy()
            merged_config.update(user_config)
            
            # Merge das api_keys
            if "api_keys" in user_config and isinstance(user_config["api_keys"], dict):
                merged_keys = DEFAULT_CONFIG["api_keys"].copy()
                merged_keys.update(user_config["api_keys"])
                merged_config["api_keys"] = merged_keys
                
            return merged_config
    except (json.JSONDecodeError, IOError):
        # Em caso de falha de leitura ou JSON corrompido, evita quebrar a aplicação
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> None:
    """
    Salva o dicionário de configurações no arquivo global ~/.goodfella_config.
    """
    config_path = get_config_path()
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
