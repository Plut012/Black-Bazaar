#!/usr/bin/env python3
"""
AI Card Trader - Streamlit Frontend
Retro-styled interface for trading cards with an AI shopkeeper
"""

import streamlit as st
import requests
import json
from typing import List, Dict

# Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS for retro styling
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Creepster&family=Cinzel:wght@400;600&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: #e8dcc6;
    }
    
    .main-header {
        font-family: 'Creepster', cursive;
        font-size: 3rem;
        color: #d4af37;
        text-align: center;
        text-shadow: 3px 3px 0px #8b4513;
        margin-bottom: 10px;
    }
    
    .subtitle {
        font-family: 'Cinzel', serif;
        font-size: 1.2rem;
        color: #cd853f;
        text-align: center;
        font-style: italic;
        margin-bottom: 30px;
    }
    
    .card-container {
        background: rgba(0, 0, 0, 0.4);
        border: 2px solid #8b4513;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .card-container:hover {
        border-color: #d4af37;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
    }
    
    .card-name {
        font-family: 'Cinzel', serif;
        font-weight: 600;
        color: #d4af37;
        font-size: 1.2rem;
        margin-bottom: 5px;
    }
    
    .card-type {
        color: #cd853f;
        font-size: 0.9rem;
        margin-bottom: 5px;
        font-style: italic;
    }
    
    .card-cost {
        background: rgba(139, 69, 19, 0.8);
        color: #fff;
        padding: 3px 8px;
        border-radius: 5px;
        font-size: 0.8rem;
        display: inline-block;
        margin-bottom: 8px;
    }
    
    .card-text {
        font-size: 0.85rem;
        color: #e8dcc6;
        line-height: 1.4;
        margin-bottom: 10px;
        border-left: 3px solid #8b4513;
        padding-left: 10px;
    }
    
    .card-pt {
        background: #8b4513;
        color: #d4af37;
        padding: 3px 8px;
        border-radius: 5px;
        font-size: 0.8rem;
        font-weight: bold;
        float: right;
        margin-bottom: 8px;
    }
    
    .card-keywords {
        color: #d4af37;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 8px;
        text-transform: uppercase;
    }
    
    .shopkeeper-message {
        background: rgba(212, 175, 55, 0.2);
        border: 2px solid #d4af37;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        font-family: 'Cinzel', serif;
        font-style: italic;
        color: #e8dcc6;
    }
    
    .user-message {
        background: rgba(139, 69, 19, 0.6);
        border: 2px solid #8b4513;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        font-family: 'Cinzel', serif;
        color: #e8dcc6;
        text-align: right;
    }
    
    .stButton > button {
        background: linear-gradient(145deg, #8b4513, #654321);
        color: #d4af37;
        border: 2px solid #8b4513;
        border-radius: 8px;
        font-family: 'Cinzel', serif;
        font-weight: 600;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(145deg, #a0522d, #8b4513);
        border-color: #d4af37;
        transform: translateY(-2px);
    }
    
    .stTextInput > div > div > input {
        background: rgba(0, 0, 0, 0.5);
        color: #e8dcc6;
        border: 2px solid #8b4513;
        border-radius: 5px;
        font-family: 'Cinzel', serif;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #d4af37;
        box-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
    }
    
    .stSelectbox > div > div > select {
        background: rgba(0, 0, 0, 0.5);
        color: #e8dcc6;
        border: 2px solid #8b4513;
        border-radius: 5px;
        font-family: 'Cinzel', serif;
    }
    
    .section-header {
        font-family: 'Cinzel', serif;
        font-size: 1.5rem;
        color: #d4af37;
        text-align: center;
        border-bottom: 2px solid #8b4513;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def display_card(card: Dict, key: str = None):
    """Display a card with retro styling, showing only essential gameplay information"""
    # Extract essential card information
    name = card.get('name', 'Unknown Card')
    mana_cost = card.get('manaCost', '{0}')
    type_line = card.get('type', 'Unknown Type')
    power = card.get('power', '')
    toughness = card.get('toughness', '')
    oracle_text = card.get('text', 'No text available.')
    keywords = card.get('keywords', [])
    
    # Format power/toughness if present
    pt_text = f"{power}/{toughness}" if power and toughness else ""
    
    # Format keywords
    keywords_text = " • ".join(keywords) if keywords else ""
    
    card_html = f"""
    <div class="card-container">
        <div class="card-name">{name}</div>
        <div class="card-cost">{mana_cost}</div>
        <div class="card-type">{type_line}</div>
        {f'<div class="card-pt">{pt_text}</div>' if pt_text else ''}
        {f'<div class="card-keywords">{keywords_text}</div>' if keywords_text else ''}
        <div class="card-text">{oracle_text}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def api_request(endpoint: str, method: str = "GET", data: Dict = None, show_errors: bool = True):
    """Make API request to backend"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            if show_errors:
                st.error(f"API Error: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        if show_errors:
            st.error("⚠️ Cannot connect to backend API. Make sure the FastAPI server is running on localhost:8000")
        return None
    except requests.exceptions.Timeout:
        if show_errors:
            st.error("⏱️ Request timed out. Please try again.")
        return None
    except Exception as e:
        if show_errors:
            st.error(f"Error: {str(e)}")
        return None

def handle_speak(message, builder_id=None):
    """Handle speaking with the shopkeeper"""
    data = {"message": message}
    if builder_id:
        data["builder"] = builder_id
    
    response = api_request("/speak", method="POST", data=data)
    if response:
        return response
    return None

def load_builders():
    """Load available builders from the API"""
    response = api_request("/api/builders")
    if response:
        return response.get("builders", [])
    return []

def main():
    # Set page config
    st.set_page_config(
        page_title="Black-Bazaar Card Emporium",
        page_icon="🃏",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_css()
    
    # Header
    st.markdown('<div class="main-header">🃏 Black-Bazaar Card Emporium</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">"Where Power Meets Its Price"</div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'selected_cards' not in st.session_state:
        st.session_state.selected_cards = []
    if 'current_inventory' not in st.session_state:
        st.session_state.current_inventory = []
    if 'selected_builder' not in st.session_state:
        st.session_state.selected_builder = None
    if 'builders' not in st.session_state:
        st.session_state.builders = []
    if 'user_message' not in st.session_state:
        st.session_state.user_message = ""
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="section-header">🎒 Your Collection</div>', unsafe_allow_html=True)
        
        if st.session_state.selected_cards:
            for i, card in enumerate(st.session_state.selected_cards):
                st.write(f"• {card.get('name', 'Unknown')}")
                if st.button(f"Remove {card.get('name', 'Card')}", key=f"remove_{i}"):
                    st.session_state.selected_cards.pop(i)
                    st.rerun()
        else:
            st.write("*No cards selected*")
        
        st.markdown("---")
        
        # Builder selection
        st.markdown('<div class="section-header">🔮 Choose Your Builder</div>', unsafe_allow_html=True)
        
        # Load builders if not already loaded
        if not st.session_state.builders:
            st.session_state.builders = load_builders()
        
        if st.session_state.builders:
            builder_options = {"None": None}
            for builder in st.session_state.builders:
                builder_options[f"{builder['name']} - {builder['specialty']}"] = builder['id']
            
            selected_builder_key = st.selectbox(
                "Select a builder to speak with:",
                options=list(builder_options.keys()),
                key="builder_selectbox"
            )
            
            st.session_state.selected_builder = builder_options[selected_builder_key]
            
            if st.session_state.selected_builder:
                # Show selected builder info
                selected_builder_info = next(
                    (b for b in st.session_state.builders if b['id'] == st.session_state.selected_builder),
                    None
                )
                if selected_builder_info:
                    st.markdown(f"""<div style="
                        background: rgba(212, 175, 55, 0.1); 
                        border: 1px solid #d4af37; 
                        border-radius: 8px; 
                        padding: 10px; 
                        margin: 10px 0;
                        font-size: 0.9rem;
                        color: #e8dcc6;">
                        <strong>{selected_builder_info['name']}</strong><br>
                        <em>{selected_builder_info['description']}</em><br>
                        <small>📍 {selected_builder_info['location']}</small>
                    </div>""", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick actions
        st.markdown('<div class="section-header">⚡ Quick Actions</div>', unsafe_allow_html=True)
        
        if st.button("🔄 Refresh Inventory"):
            st.session_state.current_inventory = []
            st.rerun()
        
        if st.button("🗑️ Clear Collection"):
            st.session_state.selected_cards = []
            st.rerun()
        
        if st.button("💬 Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="section-header">📚 Current Inventory</div>', unsafe_allow_html=True)
        
        # Search functionality
        search_query = st.text_input("🔍 Search cards...", placeholder="Enter card name, type, or description")
        
        col_search, col_random = st.columns([1, 1])
        
        with col_search:
            if st.button("Search Cards") and search_query:
                with st.spinner("🔍 Searching cards..."):
                    result = api_request("/api/cards/search", "POST", {"query": search_query, "limit": 10})
                    if result:
                        st.session_state.current_inventory = result.get('cards', [])
                        if result.get('cards'):
                            st.success(f"Found {len(result['cards'])} cards matching '{search_query}'")
                        else:
                            st.warning(f"No cards found matching '{search_query}'")
                    else:
                        st.session_state.current_inventory = []
        
        with col_random:
            if st.button("Show Random Cards"):
                with st.spinner("🎲 Loading random cards..."):
                    result = api_request("/api/cards/random/8")
                    if result:
                        st.session_state.current_inventory = result.get('cards', [])
                        if result.get('cards'):
                            st.success(f"Loaded {len(result['cards'])} random cards")
                        else:
                            st.warning("No cards available in database")
                    else:
                        st.session_state.current_inventory = []
        
        # Display cards
        if not st.session_state.current_inventory:
            # Load initial inventory
            with st.spinner("🏪 Loading initial inventory..."):
                result = api_request("/api/cards/random/6", show_errors=False)
                if result:
                    st.session_state.current_inventory = result.get('cards', [])
        
        if st.session_state.current_inventory:
            # Display cards in grid
            for i in range(0, len(st.session_state.current_inventory), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    if i + j < len(st.session_state.current_inventory):
                        card = st.session_state.current_inventory[i + j]
                        with col:
                            display_card(card, key=f"card_{i+j}")
                            if st.button(f"Add to Collection", key=f"add_{i+j}"):
                                if card not in st.session_state.selected_cards:
                                    st.session_state.selected_cards.append(card)
                                    st.success(f"Added {card.get('name', 'card')} to collection!")
                                    st.rerun()
        else:
            st.warning("No cards available. Check if the backend API is running.")
    
    with col2:
        # Dynamic header based on selected builder
        if st.session_state.selected_builder:
            builder_info = next(
                (b for b in st.session_state.builders if b['id'] == st.session_state.selected_builder),
                None
            )
            if builder_info:
                st.markdown(f'<div class="section-header">💬 Chat with {builder_info["name"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="section-header">💬 Chat with Builder</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="section-header">💬 Select a Builder to Chat</div>', unsafe_allow_html=True)
        
        # Builder section with dynamic content
        if st.session_state.selected_builder:
            builder_info = next(
                (b for b in st.session_state.builders if b['id'] == st.session_state.selected_builder),
                None
            )
            if builder_info:
                st.markdown(f'''
                <div style="background: repeating-linear-gradient(
                        90deg, #333 0, #333 10px, #111 10px, #111 20px
                    );
                    padding: 20px; border: 4px solid #555; border-radius: 10px;
                    text-align: center; margin-bottom: 30px;">
                    
                    <img src="https://via.placeholder.com/200x150.png?text={builder_info['name'].replace(' ', '+')}" 
                         alt="{builder_info['name']}" 
                         style="border: 5px solid #222; border-radius: 5px; max-height: 150px;">
                    <div style="margin-top: 10px; font-family: 'Cinzel', serif; font-style: italic; color: #cd853f;">
                        "{builder_info['description']}"
                    </div>
                    <div style="margin-top: 5px; font-size: 0.8rem; color: #8b4513;">
                        📍 {builder_info['location']}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div style="background: repeating-linear-gradient(
                    90deg, #333 0, #333 10px, #111 10px, #111 20px
                );
                padding: 20px; border: 4px solid #555; border-radius: 10px;
                text-align: center; margin-bottom: 30px;">
                
                <img src="https://via.placeholder.com/200x150.png?text=Select+Builder" 
                     alt="Select Builder" 
                     style="border: 5px solid #222; border-radius: 5px; max-height: 150px;">
                <div style="margin-top: 10px; font-family: 'Cinzel', serif; font-style: italic; color: #cd853f;">
                    "Choose a builder from the sidebar to begin..."
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Chat history
        for message in st.session_state.chat_history:
            if message.get('role') == 'builder':
                st.markdown(f'<div class="shopkeeper-message"><strong>{message.get("builder", "Builder")}:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        
        # Chat input and send button
        if st.session_state.selected_builder:
            user_input = st.text_input("💬 Your message:", placeholder="Type your message here...", key="chat_input")
            
            col_send, col_clear = st.columns([3, 1])
            
            with col_send:
                if st.button("Send Message", key="send_btn") and user_input.strip():
                    # Add user message to history
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": user_input
                    })
                    
                    # Get AI response
                    with st.spinner("🤖 Waiting for response..."):
                        response = handle_speak(user_input, st.session_state.selected_builder)
                        
                        if response:
                            st.session_state.chat_history.append({
                                "role": "builder",
                                "content": response["message"],
                                "builder": response["builder"]
                            })
                        else:
                            st.session_state.chat_history.append({
                                "role": "builder",
                                "content": "🔧 I'm having trouble connecting right now. Please try again later.",
                                "builder": "System"
                            })
                    
                    # Clear input and refresh
                    st.rerun()
            
            with col_clear:
                if st.button("Clear Chat", key="clear_chat_btn"):
                    st.session_state.chat_history = []
                    st.rerun()
        else:
            st.info("Please select a builder from the sidebar to start a conversation.")

if __name__ == "__main__":
    main()
