# 🎩 Goodfella

**Strict Pair Programmer CLI** — Um assistente de IA focado estritamente em Engenharia de Software que atua como um Pair Programmer Rigoroso e Arquiteto de Software.

## O que é?

O Goodfella analisa códigos, detecta violações de princípios (SOLID, Clean Architecture, DDD, etc.) e sugere melhorias. Ele **não altera código diretamente** — apenas aconselha.

## Características

- 🔒 **Local-First** — Processamento padrão 100% local via Ollama
- ☁️ **Multi-Provedor** — Suporte a OpenAI, Anthropic, Gemini
- 🧠 **RAG Inteligente** — Base vetorial com ChromaDB embutido
- 📂 **Isolamento por Projeto** — Contextos independentes por diretório
- 💬 **Chat Interativo** — REPL fluido no terminal com Rich

## Instalação

A maneira recomendada de instalar o Goodfella globalmente na sua máquina é utilizando o **`pipx`** (que instala a CLI em um ambiente isolado, evitando o erro de ambiente gerenciado externamente no Linux/Mac):

```bash
pipx install goodfella
```

*Alternativamente, você pode instalar via pip tradicional:*
```bash
pip install goodfella
```

## Uso

Para iniciar o assistente, basta rodar o comando na raiz do diretório do seu projeto:

```bash
goodfella
```

### Configurando o Provedor de IA (Local vs Cloud)

O Goodfella foi desenhado para ser **Local-First**. Por padrão, ele tentará se conectar ao **Ollama** rodando localmente na sua máquina (porta 11434). Essa é a recomendação para máxima privacidade, já que seu código nunca sai do seu computador.

**Como usar com o Ollama (Padrão):**
1. Certifique-se de que o Ollama está instalado e rodando no seu terminal (`ollama serve`).
2. Baixe o modelo padrão do Goodfella (Qwen 2.5 Coder):
   ```bash
   ollama pull qwen2.5-coder:7b
   ```
3. Rode o comando `goodfella` no seu projeto e a CLI se conectará automaticamente.

Se você não possui uma GPU forte ou se deseja análises arquiteturais mais profundas usando outros modelos, o Goodfella possui integrações nativas com a nuvem.

Como habilitar e usar provedores Cloud:

**Interativamente (via chat):**
Inicie o Goodfella normalmente e digite o comando `/setup`. Um menu interativo guiará você na escolha do provedor e na inserção segura da sua chave de API.

**Dica:** Uma vez dentro do assistente, utilize o comando `/status` para auditar rapidamente qual provedor de IA e modelo específico estão assumindo o controle das respostas no momento.

### Comandos Principais

| Comando | Descrição |
|---------|-----------|
| `/review` | Revisão estrita de Clean Architecture/SOLID |
| `/deep-review` | Análise completa via modelo Cloud |
| `/setup` | Assistente de configuração de provedor |
| `/status` | Saúde do sistema e provedor ativo |
| `/rule add` | Adicionar regra customizada |
| `/rebuild` | Reconstruir banco vetorial do zero |
| `/quit` | Encerrar e salvar histórico |

## Stack Técnica

- **Python** + **uv**
- **LangChain** — Orquestração de IA
- **ChromaDB** — Banco vetorial embutido
- **Rich** — Interface de terminal
- **Ollama** — LLM local (padrão)

## Licença

Proprietary / All Rights Reserved

O código-fonte é disponibilizado apenas para visualização e fins educacionais. É estritamente proibido modificar, distribuir, sublicenciar ou utilizar este projeto (ou qualquer parte dele) para fins comerciais sem autorização prévia por escrito.
