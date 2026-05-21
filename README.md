# ChessAI

Um assistente inteligente que responde perguntas sobre xadrez combinando conhecimento e análise.

## Como funciona

Combina três componentes principais:

- **RAG (Retrieval-Augmented Generation)** - Busca conhecimento em um PDF de xadrez transformado em vetores
- **Stockfish** - Engine de análise profunda para avaliar posições específicas (com notação FEN)
- **Gemini** - Modelo de linguagem que gera as respostas contextualizadas

## Tecnologias

- **LangChain** - Orquestração do pipeline RAG
- **Chroma** - Banco de dados vetorial
- **FastEmbedEmbeddings** - Embeddings eficientes
- **Stockfish** - Análise de xadrez
- **Gemini** - Modelo de linguagem
- **python-chess** - Validação de notações
- **PyPDF** - Leitura do PDF

## Visualizando em Ação

Interface da aplicação

![ChessAI Interface](./images/chess_ai.png)
![ChessAI Interface](./images/response_chess_ai.png)
![ChessAI Interface](./images/response_fen_chess_ai.png)


## Pré-requisitos

- Python 3.11+
- Stockfish (`apt install stockfish` no Linux, ou `brew install stockfish` no macOS)
- Chave da API do Google Gemini

## Instalação

1. Instale as dependências:
```bash
pip install -e .
```

2. Configure a API key (copie `.env.example` para `.env` ou crie um novo):
```
API_KEY=sua_chave_gemini_aqui
```

3. Coloque o `chess.pdf` na raiz do projeto

## Rodando

```bash
python -m chess_ai.main
```

Digite suas perguntas. Se incluir uma notação FEN, o sistema analisa com Stockfish. Sem FEN, busca contexto no PDF e responde.

**Combinando análise com conhecimento:**
```
Ask something: FEN: r1bqkb1r/pppp1ppp/2n2n2/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1
Qual abertura é essa? Como responder o ataque ao bispo?
```
O sistema identifica a abertura pelo PDF e combina com análise do engine para uma resposta completa.

---

