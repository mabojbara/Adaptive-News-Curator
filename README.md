# Adaptive News Curator

An agentic AI tool built with LangChain that learns your news preferences through feedback loops.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add your API keys to a `.env` file (`OPENAI_API_KEY` and `TAVILY_API_KEY`).

## How to Run
```bash
python -m src.main
```