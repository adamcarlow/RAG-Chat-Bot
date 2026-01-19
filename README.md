<p align="center">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/LangChain-00A3E0?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain"/>
  <img src="https://img.shields.io/badge/Groq-FF6F00?style=for-the-badge&logo=groq&logoColor=white" alt="Groq"/>
  <img src="https://img.shields.io/badge/Llama%203.3-4A90E2?style=for-the-badge" alt="Llama 3.3"/>
  <img src="https://img.shields.io/badge/RAG-Powered-brightgreen?style=for-the-badge" alt="RAG"/>
</p>

<h1 align="center">Board Game Rules Assistant</h1>

<p align="center">
  A RAG-powered Streamlit app that lets you upload board game rulebook PDFs and ask natural-language questions about setup, rules, and gameplay — powered by Groq's fast Llama 3.3 70B model.
</p>

<p align="center">
  <a href="https://github.com/adamcarlow/RAG-Chat-Bot/stargazers"><img src="https://img.shields.io/github/stars/adamcarlow/RAG-Chat-Bot?style=social" alt="Stars"></a>
  <a href="https://github.com/adamcarlow/RAG-Chat-Bot/forks"><img src="https://img.shields.io/github/forks/adamcarlow/RAG-Chat-Bot?style=social" alt="Forks"></a>
  <a href="https://github.com/adamcarlow/RAG-Chat-Bot/blob/main/LICENSE"><img src="https://img.shields.io/github/license/adamcarlow/RAG-Chat-Bot?style=flat-square" alt="License"/></a>
</p>

![Streamlit RAG Chatbot Interface]
<img width="1766" height="795" alt="Screenshot 2026-01-18 at 12 24 28 PM" src="https://github.com/user-attachments/assets/ace7ae31-c597-400e-a803-da2c50e72d47" />



## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Pre-loaded Games](#pre-loaded-games)
- [Example Questions](#example-questions)
- [Configuration](#configuration)
- [License](#license)

## Features

- 📚 **9 Pre-loaded Rulebooks** — Catan, Monopoly, Risk, Chess, Checkers, Ticket to Ride, Scrabble, Game of Life, and Clue Junior ready to query
- 📄 **Upload Your Own** — Add any board game rulebook PDF
- 🎯 **Multi-Game Queries** — Select one or multiple rulebooks to search across
- ❓ **Natural Language Q&A** — Ask questions about rules, setup, and gameplay
- 🔍 **RAG-Powered Accuracy** — Context-aware answers via Retrieval-Augmented Generation
- ⚡ **Fast & Free** — Powered by Groq's Llama 3.3 70B model
- 🖥️ **Clean Interface** — Interactive Streamlit web app

## How It Works

This app implements a classic RAG pipeline:

1. **Chunking** — PDF text is split into manageable chunks
2. **Embedding** — Chunks converted to vectors (sentence-transformers)
3. **Indexing** — Stored in FAISS for fast similarity search
4. **Retrieval** — Relevant chunks pulled for the user's question
5. **Generation** — LLM generates precise answer using only retrieved context

![RAG Pipeline Diagram](https://miro.medium.com/v2/resize:fit:1200/1*eHoJ4Y5UAgt_T2YUSZ2D6Q.png)

> *Visual overview of the Retrieval-Augmented Generation flow used in this app.*

## Tech Stack

- **Frontend**: Streamlit
- **RAG Framework**: LangChain
- **LLM**: Groq API (Llama 3.3 70B — free tier available)
- **Vector Store**: FAISS
- **Embeddings**: all-MiniLM-L6-v2 (Hugging Face)
- **PDF Handling**: PyPDF

## Prerequisites

- Python 3.8+
- Free Groq API key → [Get one here](https://console.groq.com)

## Installation

1. Clone the repo:

   ```bash
   git clone https://github.com/adamcarlow/RAG-Chat-Bot.git
   cd RAG-Chat-Bot

2. Install dependencies:

```bash
pip install -r requirements.txt
```
3. Add your Groq key (create .env file):

```
echo "GROQ_API_KEY=your-api-key-here" > .env
```
## Usage

Launch the app:
```
streamlit run gamerulesrag.py
```
Open http://localhost:8501 in your browser.

Upload a board game rulebook PDF (e.g., Catan, Ticket to Ride, Monopoly)
Wait for processing (chunking + embedding — usually quick)
Ask your question in the chat box
Get rule-based answers!

Catan Board Game Setup
Example board game setup (Catan) — the kind of content your app can now answer questions about instantly.

## Pre-loaded Games

The app comes with 9 classic board game rulebooks ready to query:

| Game | Description |
|------|-------------|
| Catan | Resource trading and settlement building |
| Monopoly | Classic property trading game |
| Risk | World domination strategy |
| Chess | Classic strategy board game |
| Checkers | Simple capture game |
| Ticket to Ride | Train route building |
| Scrabble | Word building game |
| Game of Life | Life simulation board game |
| Clue Junior | Mystery solving for kids |

## Example Questions

**Single Game:**
- "How do I set up the game?"
- "What happens when I roll doubles?"
- "Can I trade on my first turn?"
- "How do I win?"

**Cross-Game Comparisons:**
- "Compare the victory conditions between these games"
- "Which game has the longest setup?"
- "What are the differences in trading rules?"

## Configuration
Edit these in gamerulesrag.py to tune performance:
```
CHUNK_SIZE = 2000      # Characters per chunk
CHUNK_OVERLAP = 200    # Overlap between chunks
TOP_K_CHUNKS = 4       # Number of chunks to retrieve
```
## License
MIT License
Feel free to fork, modify, and share!
