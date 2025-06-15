import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import pdb
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def load_cards(file_path: str) -> List[Dict[str, Any]]:
    """Load cards from the JSON file."""
    logger.debug(f"Loading cards from {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            cards = json.load(f)
        logger.info(f"Successfully loaded {len(cards)} cards")
        return cards
    except Exception as e:
        logger.error(f"Error loading cards: {str(e)}")
        raise

def create_card_embedding(card: Dict[str, Any], model: SentenceTransformer) -> List[float]:
    """Create embedding for a card using its name and text."""
    logger.debug(f"Creating embedding for card: {card.get('name', 'Unknown')}")
    try:
        # Combine card name and text for embedding
        card_text = f"{card.get('name', '')} {card.get('text', '')}"
        embedding = model.encode(card_text)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Error creating embedding: {str(e)}")
        raise

def main():
    # Initialize Qdrant client
    logger.debug("Initializing Qdrant client...")
    pdb.set_trace()  # Breakpoint 1: Check Qdrant connection
    client = QdrantClient(
        host=os.getenv("QDRANT_HOST", "localhost"),
        port=int(os.getenv("QDRANT_PORT", 6333))
    )
    
    # Load sentence transformer model
    logger.debug("Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    pdb.set_trace()  # Breakpoint 2: Check model loading
    
    # Load cards from JSON file
    cards_file = Path("cards/mtg.json")
    cards = load_cards(str(cards_file))
    pdb.set_trace()  # Breakpoint 3: Check loaded cards
    
    # Create collection if it doesn't exist
    collection_name = "mtg_cards"
    try:
        client.get_collection(collection_name)
        logger.info(f"Collection {collection_name} already exists")
    except Exception:
        logger.info(f"Creating collection {collection_name}")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=384,  # Size of the embeddings from all-MiniLM-L6-v2
                distance=models.Distance.COSINE
            )
        )
    
    # Process cards in batches
    batch_size = 100
    for i in tqdm(range(0, len(cards), batch_size), desc="Processing cards"):
        batch = cards[i:i + batch_size]
        pdb.set_trace()  # Breakpoint 4: Check each batch
        
        # Create embeddings for the batch
        embeddings = [create_card_embedding(card, model) for card in batch]
        
        # Prepare points for upload
        points = [
            models.PointStruct(
                id=idx + i,
                vector=embedding,
                payload=card
            )
            for idx, (card, embedding) in enumerate(zip(batch, embeddings))
        ]
        
        # Upload points to Qdrant
        client.upsert(
            collection_name=collection_name,
            points=points
        )
        logger.info(f"Uploaded batch {i//batch_size + 1}")

if __name__ == "__main__":
    main() 
