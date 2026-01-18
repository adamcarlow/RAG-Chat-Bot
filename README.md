# Board Game Rules Assistant

A RAG-powered Streamlit application that helps you understand board game rules by answering questions about uploaded rulebook PDFs.

## Features

- Upload any board game rulebook (PDF)
- Ask natural language questions about rules, setup, and gameplay
- RAG pipeline for accurate, context-aware answers
- Free to run using Groq's Llama 3.3 70B model

## How It Works

This app uses Retrieval-Augmented Generation (RAG):

1. **Chunking** - PDF is split into smaller text chunks
2. **Embedding** - Chunks are converted to vectors using sentence-transformers
3. **Indexing** - Vectors are stored in a FAISS vector store
4. **Retrieval** - When you ask a question, the most relevant chunks are found
5. **Generation** - Only relevant chunks are sent to the LLM for answering

## Tech Stack

- **Streamlit** - Web interface
- **LangChain** - RAG orchestration
- **Groq** - Free LLM API (Llama 3.3 70B)
- **FAISS** - Vector store for similarity search
- **HuggingFace** - Embeddings (all-MiniLM-L6-v2)
- **PyPDF** - PDF text extraction

## Prerequisites

- Python 3.8+
- Groq API key (free at https://console.groq.com)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/adamcarlow/RAG-Chat-Bot.git
cd RAG-Chat-Bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Groq API key:
```bash
echo "GROQ_API_KEY=your-api-key-here" > .env
```

## Usage

Run the app:
```bash
streamlit run gamerulesrag.py
```

Then open http://localhost:8501 in your browser.

1. Upload a board game rulebook PDF
2. Wait for processing (chunking & embedding)
3. Type your rules question
4. Get an answer based on the rulebook

### Example Questions

- "How do I set up the game?"
- "What happens when I roll doubles?"
- "Can I trade on my first turn?"
- "How do I win?"

## Configuration

You can adjust RAG settings in `gamerulesrag.py`:

```python
CHUNK_SIZE = 2000      # Characters per chunk
CHUNK_OVERLAP = 200    # Overlap between chunks
TOP_K_CHUNKS = 4       # Number of chunks to retrieve
```

## License

MIT License
