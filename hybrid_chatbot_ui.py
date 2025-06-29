#!/usr/bin/env python3
"""
Beautiful Streamlit UI for Hybrid Memory Medical Chatbot
Clean, readable interface with good color choices and typography.
"""

import streamlit as st
import asyncio
from datetime import datetime
from final_hybrid_chatbot import FinalHybridChatbot

# Page configuration
st.set_page_config(
    page_title="🩺 Medical Assistant AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better readability and colors
st.markdown("""
<style>
    /* Main background and text colors */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .main-header {
        color: #2c3e50;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #3498db;
        margin-bottom: 2rem;
        font-weight: 600;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
        color: #1565c0;
    }
    
    .assistant-message {
        background-color: #f1f8e9;
        border-left-color: #4caf50;
        color: #2e7d32;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #fff3e0;
        border: 1px solid #ff9800;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #e65100;
    }
    
    .success-box {
        background-color: #e8f5e8;
        border: 1px solid #4caf50;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #2e7d32;
    }
    
    .warning-box {
        background-color: #fff3e0;
        border: 1px solid #ff9800;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #e65100;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #2c3e50;
        color: white;
    }
    
    /* Memory display */
    .memory-display {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        color: #495057;
    }
    
    /* Status indicators */
    .status-online {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-offline {
        color: #dc3545;
        font-weight: bold;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #3498db;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #2980b9;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'chatbot_initialized' not in st.session_state:
    st.session_state.chatbot_initialized = False

def initialize_chatbot():
    """Initialize the hybrid memory chatbot"""
    try:
        if st.session_state.chatbot is None:
            with st.spinner("🤖 Initializing Hybrid Memory Chatbot..."):
                st.session_state.chatbot = FinalHybridChatbot()
                st.session_state.chatbot_initialized = True
                return True
    except Exception as e:
        st.error(f"❌ Failed to initialize chatbot: {e}")
        return False
    return True

def display_chat_messages():
    """Display chat messages with proper styling"""
    for message in st.session_state.chat_messages:
        if message["role"] == "user":
            st.markdown(f'''
            <div class="chat-message user-message">
                <strong>👤 You:</strong> {message["content"]}
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class="chat-message assistant-message">
                <strong>🩺 Assistant:</strong> {message["content"]}
            </div>
            ''', unsafe_allow_html=True)

def display_patient_info():
    """Display current patient information"""
    if st.session_state.chatbot and st.session_state.chatbot.has_name:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f'''
            <div class="success-box">
                <strong>👤 Patient:</strong><br>
                {st.session_state.chatbot.patient_name}
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''
            <div class="info-box">
                <strong>💬 Exchanges:</strong><br>
                {len(st.session_state.chatbot.conversation_history)}
            </div>
            ''', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f'''
            <div class="success-box">
                <strong>🧠 Memory:</strong><br>
                <span class="status-online">● Active</span>
            </div>
            ''', unsafe_allow_html=True)

def display_memory_context():
    """Display patient memory context"""
    if st.session_state.chatbot and st.session_state.chatbot.has_name:
        # Add refresh button for visits
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 📅 Recent Visits")
        with col2:
            if st.button("🔄 Refresh", key="refresh_visits"):
                st.rerun()

        # Show recent visits prominently with real-time updates
        episodic_info = st.session_state.chatbot.get_episodic_memory_direct()
        if episodic_info != "No previous visits found":
            st.markdown(f'''
            <div class="success-box">
                <strong>✅ Visit Memory Active - Patient: {st.session_state.chatbot.patient_name}</strong><br>
                {episodic_info.replace(chr(10), '<br>')}
            </div>
            ''', unsafe_allow_html=True)
        else:
            # Show when no visits yet
            st.markdown(f'''
            <div class="info-box">
                <strong>⏳ No visits recorded yet for {st.session_state.chatbot.patient_name}</strong><br>
                Mention symptoms like "I have back pain" to see visits appear here!
            </div>
            ''', unsafe_allow_html=True)

        # Show full medical records in expandable section
        with st.expander("🧠 Complete Patient Medical Records", expanded=False):
            context = st.session_state.chatbot.get_patient_context()
            st.markdown(f'''
            <div class="memory-display">
                {context.replace(chr(10), '<br>')}
            </div>
            ''', unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🩺 Hybrid Memory Medical Assistant</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎛️ Control Panel")
        
        # Initialize chatbot button
        if st.button("🚀 Initialize Chatbot", type="primary"):
            initialize_chatbot()
        
        # Status display
        if st.session_state.chatbot_initialized:
            st.markdown('<p class="status-online">● Chatbot Online</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-offline">● Chatbot Offline</p>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # New session button
        if st.button("🔄 New Session"):
            st.session_state.chatbot = None
            st.session_state.chat_messages = []
            st.session_state.chatbot_initialized = False
            st.rerun()
        
        st.markdown("---")
        
        # Sample patients
        st.markdown("### 👥 Sample Patients")
        st.markdown("""
        <div style="color: #495057; font-size: 0.9rem;">
        Try these existing patients:
        <br>• <strong>John Smith</strong> - Heart issues
        <br>• <strong>Sarah Johnson</strong> - Diabetes, migraines  
        <br>• <strong>Michael Brown</strong> - Asthma
        <br>• <strong>Emily Davis</strong> - Mental health
        <br>• <strong>Robert Wilson</strong> - Arthritis
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Memory systems status
        st.markdown("### 🧠 Memory Systems")
        st.markdown("""
        <div style="color: #495057; font-size: 0.9rem;">
        <span class="status-online">● Episodic Memory</span><br>
        <span class="status-online">● Behavioral Memory</span><br>
        <span class="status-online">● Medical Facts</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    if not st.session_state.chatbot_initialized:
        st.markdown('''
        <div class="warning-box">
            <h3>🚀 Welcome to Your Medical Assistant!</h3>
            <p>Click <strong>"Initialize Chatbot"</strong> in the sidebar to start.</p>
            <p>This chatbot has access to patient medical records and can:</p>
            <ul>
                <li>Remember your medical history</li>
                <li>Track your symptoms and visits</li>
                <li>Store your preferences</li>
                <li>Provide personalized care</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
        return
    
    # Patient information display
    display_patient_info()
    
    # Chat interface
    st.markdown("### 💬 Conversation")
    
    # Display chat messages
    display_chat_messages()
    
    # Add initial greeting if no messages
    if not st.session_state.chat_messages:
        st.markdown(f'''
        <div class="chat-message assistant-message">
            <strong>🩺 Assistant:</strong> Hello! I'm your medical assistant with access to your complete medical records. What's your name?
        </div>
        ''', unsafe_allow_html=True)
    
    # Chat input with auto-clear functionality
    if 'input_counter' not in st.session_state:
        st.session_state.input_counter = 0

    user_input = st.text_input(
        "💬 Type your message:",
        placeholder="Tell me your name or describe your health concerns...",
        key=f"chat_input_{st.session_state.input_counter}",
        help="💡 Tip: Press Enter or click Send to submit your message"
    )
    
    # Send button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        send_button = st.button("📤 Send", type="primary")
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_messages = []
            st.rerun()
    
    # Process message (either button click or Enter key)
    if (send_button and user_input) or (user_input and user_input != st.session_state.get('last_input', '')):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": user_input})

        # Get chatbot response
        with st.spinner("🤔 Processing your message..."):
            try:
                response = st.session_state.chatbot.process_message(user_input)
                st.session_state.chat_messages.append({"role": "assistant", "content": response})

                # Clear input by incrementing counter (creates new input field)
                st.session_state.input_counter += 1
                st.session_state.last_input = user_input

                # Force UI refresh to show updated visit information
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error processing message: {e}")
    
    # Display memory context
    display_memory_context()
    
    # Footer
    st.markdown("---")
    st.markdown('''
    <div style="text-align: center; color: #6c757d; font-size: 0.9rem;">
        🩺 Hybrid Memory Medical Assistant | Powered by AI with Semantic, Episodic & Behavioral Memory
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
