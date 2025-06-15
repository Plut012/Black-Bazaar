#!/usr/bin/env python3
"""
AI Card Trader - Streamlit Frontend
Retro-styled interface for trading cards with an AI shopkeeper
"""

import streamlit as st
import requests
import json
import time
from typing import List, Dict
import pandas as pd

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
    
    .card-value {
        background: #8b4513;
        color: #d4af37;
        padding: 3px 8px;
        border-radius: 5px;
        font-size: 0.8rem;
        font-weight: bold;
        float: right;
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

def render_shop_ui(cards: List[Dict], on_speak_callback):
    """Render the AI card trader shop interface"""
    load_css()  # Assuming this loads your retro CSS

    # Shopkeeper section with bars and image
    st.markdown('''
    <div style="background: repeating-linear-gradient(
            90deg, #333 0, #333 10px, #111 10px, #111 20px
        );
        padding: 20px; border: 4px solid #555; border-radius: 10px;
        text-align: center; margin-bottom: 30px;">
        
        <img src="https://via.placeholder.com/200x150.png?text=Shopkeeper" 
             alt="Shopkeeper" 
             style="border: 5px solid #222; border-radius: 5px; max-height: 150px;">
        <div style="margin-top: 10px; font-family: 'Cinzel', serif; font-style: italic; color: #cd853f;">
            "What do you want, stranger?"
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # Card display area (messy table)
    st.markdown('''
    <div style="background: #3e2f1c; 
                border: 4px solid #8b4513; 
                padding: 20px; 
                border-radius: 12px;
                box-shadow: inset 0 0 20px #000;
                margin-bottom: 30px;">
        <div style="text-align: center; font-family: 'Cinzel', serif; font-size: 1.4rem; color: #d4af37; margin-bottom: 20px;">
            Cards on the Table
        </div>
    ''', unsafe_allow_html=True)

    for i, card in enumerate(cards):
        rotation = (-5 + i * 3) % 10 - 5
        st.markdown(f'''
        <div style="display: inline-block; transform: rotate({rotation}deg); margin: 10px;">
        ''', unsafe_allow_html=True)
        display_card(card)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Speak button
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    if st.button("💬 Speak"):
        on_speak_callback()
    st.markdown('</div>', unsafe_allow_html=True)

def handle_speak():
    response = api_request("/speak", method="POST")
    if response:
        st.markdown(f'''
        <div class="shopkeeper-message">{response["message"]}</div>
        ''', unsafe_allow_html=True)

# cards = api_request("/shop/cards") or []
# render_shop_ui(cards, handle_speak)

def display_card(card: Dict, key: str = None):
    """Display a card with retro styling"""
    card_html = f"""
    <div class="card-container">
        <div class="card-name">{card.get('name', 'Unknown Card')}</div>
        <div class="card-type">{card.get('type_line', 'Unknown Type')}</div>
        <div class="card-cost">{card.get('mana_cost', '{0}')}</div>
        <div class="card-value">Value: {card.get('trade_value', 0)}</div>
        <div class="card-text">{card.get('oracle_text', 'No text available.')}</div>
        {f'<div style="font-style: italic; color: #cd853f; font-size: 0.8rem;">"{card.get("flavor_text", "")}"</div>' if card.get('flavor_text') else ''}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def api_request(endpoint: str, method: str = "GET", data: Dict = None):
    """Make API request to backend"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to backend API. Make sure the FastAPI server is running on localhost:8000")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def main():
    # Set page config
    st.set_page_config(
        page_title="Grimjaw's Card Emporium",
        page_icon="🃏",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_css()
    
    # Header
    st.markdown('<div class="main-header">🃏 Grimjaw\'s Card Emporium</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">"Ancient Cards, Eternal Value"</div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'selected_cards' not in st.session_state:
        st.session_state.selected_cards = []
    if 'current_inventory' not in st.session_state:
        st.session_state.current_inventory = []
    
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
                with st.spinner("Searching cards..."):
                    result = api_request("/api/cards/search", "POST", {"query": search_query, "limit": 10})
                    if result:
                        st.session_state.current_inventory = result.get('cards', [])
        
        with col_random:
            if st.button("Show Random Cards"):
                with st.spinner("Loading random cards..."):
                    result = api_request("/api/cards/random/8")
                    if result:
                        st.session_state.current_inventory = result.get('cards', [])
        
        # Display cards
        if not st.session_state.current_inventory:
            # Load initial inventory
            result = api_request("/api/cards/random/6")
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
        st.markdown('<div class="section-header">💬 Chat with Grimjaw</div>', unsafe_allow_html=True)
        
        # Chat history
        chat_container = st.container()
        with chat_container:
