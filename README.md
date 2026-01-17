# PDF Question Answering App

A Streamlit web application that lets you ask questions about PDF documents using a local Llama 3.2 model via Ollama.

## Features

- Upload any PDF document
- Ask natural language questions about the content
- Get AI-powered answers using Llama 3.2 (3B)
- Runs completely locally - no data leaves your computer

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- Llama 3.2 model pulled: `ollama pull llama3.2:3b`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/adamcarlow/pdf-qa-app.git
cd pdf-qa-app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure Ollama is running with the Llama 3.2 model:
```bash
ollama pull llama3.2:3b
ollama serve
```

## Usage

Run the app:
```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

1. Upload a PDF file
2. Type your question
3. Click "Get Answer"

## How It Works

1. PDF text is extracted using PyPDF
2. Your question and the document context are sent to Llama 3.2 via Ollama
3. The model generates an answer based only on the document content

## Tech Stack

- **Streamlit** - Web interface
- **LangChain** - LLM orchestration
- **Ollama** - Local LLM inference
- **Llama 3.2 (3B)** - Language model
- **PyPDF** - PDF text extraction

## License

MIT License
