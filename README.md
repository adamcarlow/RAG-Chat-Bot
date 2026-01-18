# Board Game Rules Assistant

A Streamlit web application that helps you understand board game rules by answering questions about uploaded rulebook PDFs, powered by xAI's Grok model.

## Features

- Upload any board game rulebook (PDF)
- Ask natural language questions about rules, setup, and gameplay
- Get clear, accurate answers powered by Grok
- Example questions provided to help you get started

## Prerequisites

- Python 3.8+
- xAI API key (get one at https://console.x.ai)

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

3. Create a `.env` file with your xAI API key:
```bash
echo "XAI_API_KEY=your-api-key-here" > .env
```

## Usage

Run the app:
```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

1. Upload a board game rulebook PDF
2. Type your rules question
3. Click "Get Answer"

### Example Questions

- "How do I set up the game?"
- "What happens when I roll doubles?"
- "Can I trade on my first turn?"
- "How do I win?"

## How It Works

1. PDF text is extracted using PyPDF
2. Your question and the rulebook context are sent to Grok via xAI's API
3. The model generates an answer based only on the rulebook content

## Tech Stack

- **Streamlit** - Web interface
- **LangChain** - LLM orchestration
- **xAI Grok** - Language model
- **PyPDF** - PDF text extraction

## Configuration

You can change the model in `app.py`:
```python
MODEL_NAME = "grok-4-1-fast-reasoning"  # Options: "grok-4", "grok-3-latest", "grok-3-fast"
```

## License

MIT License
