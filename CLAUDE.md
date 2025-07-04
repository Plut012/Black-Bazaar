# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Black-Bazaar is a dark fantasy AI card trader application featuring:
- **Backend**: FastAPI server with Qdrant vector database for card storage and retrieval
- **Frontend**: Streamlit-based retro-themed interface for trading cards with an AI shopkeeper
- **AI System**: Integration with Ollama/LLMs for intelligent card recommendations and shopkeeper interactions
- **Card Data**: MTG card ingestion and semantic search capabilities

## Architecture

### Core Components
- `main.py`: FastAPI backend server with basic health endpoints
- `store.py`: Streamlit frontend with retro card trading interface
- `ingest_cards.py`: Card data ingestion pipeline using Qdrant vector database
- `prompts/`: AI system prompts for different character archetypes
  - `builders.py`: Character definitions for card crafters/traders
  - `context.py`: Game rules and interaction frameworks

### Data Flow
1. Cards are ingested via `ingest_cards.py` into Qdrant vector database
2. Frontend queries backend for card search and recommendations
3. AI system uses character prompts to generate shopkeeper responses
4. Vector similarity search enables semantic card matching

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables (create .env file)
OLLAMA_HOST=localhost
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### Running the Application
```bash
# Start services with Docker Compose
docker-compose up

# Run backend only
uvicorn main:app --host 0.0.0.0 --port 8000

# Run frontend only
streamlit run store.py --server.port=3000 --server.address=0.0.0.0

# Ingest card data
python ingest_cards.py
```

## Key Technical Details

### Vector Database Integration
- Uses Qdrant for semantic card search with sentence-transformers embeddings
- Card data processed to extract essential gameplay information
- Embedding model: `all-MiniLM-L6-v2` (384-dimensional vectors)

### AI Character System
- Multiple character archetypes with distinct personalities and speech patterns
- Prompts designed for immersive roleplaying experiences
- Characters include: Grumpy Underground Trader, Augmented Artificer, Corrupted Druid, Fallen Cleric, Void Archivist, Mountain Smith

### Frontend Features
- Custom CSS for retro/dark fantasy aesthetic
- Card collection management
- Real-time chat with AI shopkeeper
- Responsive grid layout for card display

## File Structure Notes

- Card data expected in `cards/mtg.json` format
- Environment variables loaded from `.env` file
- Docker setup with separate frontend/backend containers
- Qdrant database runs as separate service

## API Endpoints (Expected)
- `/api/cards/search` - Semantic card search
- `/api/cards/random/{count}` - Random card selection  
- `/speak` - AI shopkeeper interaction

## Dependencies
- **FastAPI**: Web framework for backend API
- **Streamlit**: Frontend framework with custom styling
- **Qdrant**: Vector database for card storage
- **Sentence Transformers**: For card embeddings
- **Ollama**: LLM integration for AI responses

7 Claude rules
1. First think through the problem, read the codebase for relevant files, and write a plan to tasks/todo.md.
2. The plan should have a list of todo items that you can check off as you complete them
3. Before you begin working, check in with me and I will verify the plan.
4. Then, begin working on the todo items, marking them as complete as you go.
5. Please every step of the way just give me a high level explanation of what changes you made
6. Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.
7. Finally, add a review section to the [todo.md] file with a summary of the changes you made and any other relevant information.
