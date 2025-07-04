from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import logging
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import httpx
import random
import asyncio

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Card Trader API")

# Initialize global clients
qdrant_client = None
embedding_model = None
ollama_client = None

# Pydantic models
class CardSearchRequest(BaseModel):
    query: str
    limit: int = 10

class SpeakRequest(BaseModel):
    message: str
    builder: Optional[str] = None

class CardResponse(BaseModel):
    cards: List[Dict]
    total: int

class SpeakResponse(BaseModel):
    message: str
    builder: str

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients on startup
@app.on_event("startup")
async def startup_event():
    global qdrant_client, embedding_model, ollama_client
    
    try:
        # Initialize Qdrant client
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
        qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
        logger.info(f"Connected to Qdrant at {qdrant_host}:{qdrant_port}")
        
        # Initialize embedding model
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Loaded embedding model")
        
        # Initialize Ollama client
        ollama_host = os.getenv("OLLAMA_HOST", "localhost")
        ollama_port = os.getenv("OLLAMA_PORT", "11434")
        ollama_client = httpx.AsyncClient(base_url=f"http://{ollama_host}:{ollama_port}")
        logger.info(f"Connected to Ollama at {ollama_host}:{ollama_port}")
        
    except Exception as e:
        logger.error(f"Failed to initialize clients: {e}")
        # Don't crash the app, just log the error

@app.on_event("shutdown")
async def shutdown_event():
    global ollama_client
    if ollama_client:
        await ollama_client.aclose()

@app.get("/")
async def root():
    return {"message": "Welcome to AI Card Trader API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/cards/search", response_model=CardResponse)
async def search_cards(request: CardSearchRequest):
    """Search for cards using semantic similarity"""
    global qdrant_client, embedding_model
    
    if not qdrant_client or not embedding_model:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Create embedding for the search query
        query_embedding = embedding_model.encode(request.query).tolist()
        
        # Search in Qdrant
        search_result = qdrant_client.search(
            collection_name="mtg_cards",
            query_vector=query_embedding,
            limit=request.limit,
            with_payload=True
        )
        
        # Extract card data from search results
        cards = [hit.payload for hit in search_result]
        
        return CardResponse(cards=cards, total=len(cards))
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

@app.get("/api/cards/random/{count}", response_model=CardResponse)
async def get_random_cards(count: int):
    """Get random cards from the collection"""
    global qdrant_client
    
    if not qdrant_client:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get total count of cards
        collection_info = qdrant_client.get_collection("mtg_cards")
        total_cards = collection_info.points_count
        
        if total_cards == 0:
            return CardResponse(cards=[], total=0)
        
        # Generate random IDs
        random_ids = random.sample(range(total_cards), min(count, total_cards))
        
        # Retrieve cards by IDs
        cards = []
        for card_id in random_ids:
            try:
                point = qdrant_client.retrieve(
                    collection_name="mtg_cards",
                    ids=[card_id],
                    with_payload=True
                )
                if point:
                    cards.append(point[0].payload)
            except Exception as e:
                logger.warning(f"Failed to retrieve card {card_id}: {e}")
                continue
        
        return CardResponse(cards=cards, total=len(cards))
        
    except Exception as e:
        logger.error(f"Random cards error: {e}")
        # Return empty response instead of error for better UX
        return CardResponse(cards=[], total=0)

@app.get("/api/builders")
async def get_builders():
    """Get available builders"""
    builders = [
        {
            "id": "grimwick",
            "name": "Grimwick \"The Alterist\"",
            "description": "A grungy, grumpy shadow merchant operating a cramped, dimly-lit stall",
            "specialty": "Shadow alterations and forbidden modifications",
            "location": "Black-Bazaar Underground",
            "image": "grimwick.jpg"
        },
        {
            "id": "keth_vex",
            "name": "Keth Vex, the Cardwright",
            "description": "A scarred, chrome-fingered artificer from the Undercity",
            "specialty": "Surgical card modifications and augmentations",
            "location": "Undercity Forge",
            "image": "keth_vex.jpg"
        },
        {
            "id": "myriana",
            "name": "Myriana Thornweave",
            "description": "An ancient druidess from the Bleeding Grove",
            "specialty": "Organic card evolution and symbiotic growth",
            "location": "Bleeding Grove",
            "image": "myriana.jpg"
        },
        {
            "id": "cassius",
            "name": "Hierophant Cassius Vane",
            "description": "A fallen high cleric from the Bone Sanctum",
            "specialty": "Spiritual corruption and divine inversions",
            "location": "Bone Sanctum",
            "image": "cassius.jpg"
        },
        {
            "id": "xethara",
            "name": "Magister Xethara Null",
            "description": "An ancient scholar-mage from the Infinite Archive",
            "specialty": "Temporal excavation and reality manipulation",
            "location": "Infinite Archive",
            "image": "xethara.jpg"
        },
        {
            "id": "korven",
            "name": "Korven Ironheart",
            "description": "The legendary Last Smith of Mount Korthak",
            "specialty": "Pure elemental forging and truth crafting",
            "location": "Everburning Forge",
            "image": "korven.jpg"
        },
        {
            "id": "had",
            "name": "Had, the Thorn Queen",
            "description": "Ancient sorceress ruler of the Shadowbriar",
            "specialty": "Primal magic and elemental dominion",
            "location": "Shadowbriar",
            "image": "had.jpg"
        }
    ]
    return {"builders": builders}

@app.post("/speak", response_model=SpeakResponse)
async def speak_with_builder(request: SpeakRequest):
    """Speak with a builder character"""
    global ollama_client
    
    if not ollama_client:
        raise HTTPException(status_code=503, detail="AI service not available")
    
    # Default to grimwick if no builder specified
    builder_id = request.builder or "grimwick"
    
    # Import character prompts
    from prompts.builders import grumpy_underground, edgy_underground, grove_girl, cleric, void, smith, had
    
    # Map builder IDs to their prompts
    builder_prompts = {
        "grimwick": grumpy_underground,
        "keth_vex": edgy_underground,
        "myriana": grove_girl,
        "cassius": cleric,
        "xethara": void,
        "korven": smith,
        "had": had
    }
    
    builder_names = {
        "grimwick": "Grimwick",
        "keth_vex": "Keth Vex",
        "myriana": "Myriana",
        "cassius": "Cassius",
        "xethara": "Xethara",
        "korven": "Korven",
        "had": "Had"
    }
    
    if builder_id not in builder_prompts:
        raise HTTPException(status_code=400, detail="Unknown builder")
    
    try:
        # Get the character prompt
        system_prompt = builder_prompts[builder_id]
        
        # Create the chat completion request
        chat_request = {
            "model": "llama3.1",  # Default model, can be configurable
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ],
            "stream": False
        }
        
        # Call Ollama API
        response = await ollama_client.post("/api/chat", json=chat_request)
        
        if response.status_code != 200:
            raise HTTPException(status_code=503, detail="AI service error")
        
        result = response.json()
        ai_response = result.get("message", {}).get("content", "I cannot respond right now.")
        
        return SpeakResponse(message=ai_response, builder=builder_names[builder_id])
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        # Return a fallback response instead of crashing
        fallback_responses = {
            "grimwick": "*grumbles and waves dismissively* Can't talk right now, kid. Come back later.",
            "keth_vex": "*chrome fingers tap impatiently* Systems offline. Return when the connections are stable.",
            "myriana": "*vines rustle with annoyance* The grove whispers of technical difficulties, little seedling.",
            "cassius": "*sighs heavily* The divine channels are... temporarily disrupted, my child.",
            "xethara": "*adjusts spectacles* Temporal communications are experiencing interference patterns.",
            "korven": "*hammer strikes echo disapproval* ...",
            "had": "*waves dismissively* Technical difficulties bore me, darling. Try again later."
        }
        
        return SpeakResponse(
            message=fallback_responses.get(builder_id, "I'm having trouble connecting right now."),
            builder=builder_names[builder_id]
        )

# Simple in-memory session storage (in production, use Redis or database)
user_sessions = {}

class UserSession(BaseModel):
    user_id: str
    collection: List[Dict] = []
    progress: Dict = {}
    last_activity: float = 0

@app.post("/api/collection/add")
async def add_to_collection(user_id: str, card: Dict):
    """Add a card to user's collection"""
    import time
    
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession(user_id=user_id, last_activity=time.time())
    
    user_session = user_sessions[user_id]
    
    # Check if card already exists in collection
    if not any(c.get('name') == card.get('name') for c in user_session.collection):
        user_session.collection.append(card)
        user_session.last_activity = time.time()
        return {"success": True, "message": "Card added to collection"}
    else:
        return {"success": False, "message": "Card already in collection"}

@app.get("/api/collection/{user_id}")
async def get_collection(user_id: str):
    """Get user's collection"""
    if user_id not in user_sessions:
        return {"cards": [], "total": 0}
    
    user_session = user_sessions[user_id]
    return {"cards": user_session.collection, "total": len(user_session.collection)}

@app.delete("/api/collection/{user_id}/{card_name}")
async def remove_from_collection(user_id: str, card_name: str):
    """Remove a card from user's collection"""
    import time
    
    if user_id not in user_sessions:
        return {"success": False, "message": "User session not found"}
    
    user_session = user_sessions[user_id]
    
    # Find and remove the card
    for i, card in enumerate(user_session.collection):
        if card.get('name') == card_name:
            user_session.collection.pop(i)
            user_session.last_activity = time.time()
            return {"success": True, "message": "Card removed from collection"}
    
    return {"success": False, "message": "Card not found in collection"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 