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
            data = json.load(f)
            logger.debug(f"Loaded data type: {type(data)}")
            
            # If data is a list, it's already a list of cards
            if isinstance(data, list):
                logger.info(f"Found {len(data)} cards in direct list format")
                return data
                
            # If data is a dict, check for expected structure
            if isinstance(data, dict):
                logger.debug(f"Data keys: {list(data.keys())}")
                if 'data' in data:
                    all_cards = []
                    for set_code, set_data in data['data'].items():
                        logger.debug(f"Processing set {set_code}")
                        logger.debug(f"Set data type: {type(set_data)}")
                        
                        # If set_data is a list, it's a list of cards
                        if isinstance(set_data, list):
                            logger.debug(f"Found {len(set_data)} cards in set {set_code}")
                            all_cards.extend(set_data)
                        # If set_data is a dict, check for cards array
                        elif isinstance(set_data, dict):
                            logger.debug(f"Set {set_code} keys: {list(set_data.keys())}")
                            if 'cards' in set_data:
                                cards = set_data['cards']
                                logger.debug(f"Found {len(cards)} cards in set {set_code}")
                                all_cards.extend(cards)
                            # Check if the set data itself is a card
                            elif all(key in set_data for key in ['name', 'type']):
                                logger.debug(f"Found card: {set_data.get('name')}")
                                all_cards.append(set_data)
                    
                    logger.info(f"Successfully loaded {len(all_cards)} cards from all sets")
                    return all_cards
                else:
                    logger.error("No 'data' key found in JSON structure")
                    logger.debug(f"Available keys: {list(data.keys())}")
            else:
                logger.error(f"Unexpected data type: {type(data)}")
            
            raise ValueError("Invalid MTG JSON format")
    except Exception as e:
        logger.error(f"Error loading cards: {str(e)}")
        raise

def create_card_embedding(card: Dict[str, Any], model: SentenceTransformer) -> List[float]:
    """Create embedding for a card using its name, type, and text."""
    logger.debug(f"Creating embedding for card: {card.get('name', 'Unknown')}")
    try:
        # Get keywords safely, handling both string and list formats
        keywords = []
        if 'keywords' in card:
            if isinstance(card['keywords'], list):
                keywords = card['keywords']
            elif isinstance(card['keywords'], str):
                keywords = [card['keywords']]
        
        # Combine essential card information for embedding
        card_text = f"{card.get('name', '')} {card.get('type', '')} {card.get('text', '')} {' '.join(keywords)}"
        embedding = model.encode(card_text)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Error creating embedding: {str(e)}")
        raise

def process_card(card: Dict[str, Any]) -> Dict[str, Any]:
    """Process a card to extract only essential gameplay information."""
    logger.debug(f"Processing card: {card.get('name', 'Unknown')}")
    try:
        # Get keywords, handling both string and list formats
        keywords = []
        if 'keywords' in card:
            if isinstance(card['keywords'], list):
                keywords = card['keywords']
            elif isinstance(card['keywords'], str):
                keywords = [card['keywords']]
        
        # Get colors, ensuring it's a list
        colors = card.get('colors', [])
        if isinstance(colors, str):
            colors = [colors]
            
        processed = {
            'name': card.get('name', ''),
            'manaCost': card.get('manaCost', '{0}'),
            'type': card.get('type', ''),
            'power': card.get('power', ''),
            'toughness': card.get('toughness', ''),
            'text': card.get('text', ''),
            'keywords': keywords,
            'colors': colors,
            'manaValue': card.get('manaValue', 0)
        }
        logger.debug(f"Processed card: {processed['name']}")
        return processed
    except Exception as e:
        logger.error(f"Error processing card {card.get('name', 'Unknown')}: {str(e)}")
        raise

def main():
    # Initialize Qdrant client
    logger.debug("Initializing Qdrant client...")
    client = QdrantClient(
        host=os.getenv("QDRANT_HOST", "localhost"),
        port=int(os.getenv("QDRANT_PORT", 6333))
    )
    
    # Load sentence transformer model
    logger.debug("Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Load cards from JSON file
    cards_file = Path("cards/mtg.json")
    cards = load_cards(str(cards_file))
    
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
        
        # Process cards to extract essential information
        processed_cards = [process_card(card) for card in batch]
        
        # Create embeddings for the batch using processed cards
        embeddings = [create_card_embedding(card, model) for card in processed_cards]
        
        # Prepare points for upload
        points = [
            models.PointStruct(
                id=idx + i,
                vector=embedding,
                payload=card
            )
            for idx, (card, embedding) in enumerate(zip(processed_cards, embeddings))
        ]
        
        # Upload points to Qdrant
        client.upsert(
            collection_name=collection_name,
            points=points
        )
        logger.info(f"Uploaded batch {i//batch_size + 1}")

if __name__ == "__main__":
    main() 
