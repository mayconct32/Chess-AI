import logging
import streamlit as st

from chess_ai.main import (
    initialize_database,
    initialize_engine,
    request_model,
    create_prompt,
    connection_model
)


logger = logging.getLogger(__name__)

MAX_MESSAGES = 100
MAX_MESSAGE_LENGTH = 3000


def initialize_session_state() -> bool:
    """
    Initialize session state variables safely.
    
    Returns:
        bool: True if initialization successful, False otherwise
    """
    try:
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "db" not in st.session_state:
            with st.spinner("Initializing database..."):
                st.session_state.db = initialize_database()
        
        if "engine" not in st.session_state:
            with st.spinner("Initializing chess engine..."):
                st.session_state.engine = initialize_engine()

        if "model" not in st.session_state:
            with st.spinner("Initializing AI model..."):
                st.session_state.model = connection_model()
        
        logger.info("Session state initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize session state: {e}")
        st.error(f"Initialization failed: {str(e)}")
        st.error("Please check your configuration and try again.")
        st.stop()
        return False


initialize_session_state()

st.set_page_config(page_title="Chess AI", page_icon="♟️", layout="wide")

st.title(":green[Chess AI] ♟️")
st.write("Your AI assistant specialized in Chess")

# chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message["avatar"]):
        st.markdown(message["content"])

user_message = st.chat_input("Ask something about chess:")

if user_message:
    if len(user_message) > MAX_MESSAGE_LENGTH:
        st.warning(f" Message too long! Maximum {MAX_MESSAGE_LENGTH} characters.")
        st.stop()
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_message)
    
    # Add to message history
    st.session_state.messages.append({
        "role": "user",
        "content": user_message,
        "avatar": "👤"
    })
    
    try:
        prompt = create_prompt(user_message, st.session_state.engine, st.session_state.db)
        
        with st.spinner("Chess AI is thinking...", show_time=True):
            with st.chat_message("ai", avatar="♟️"):
                response_placeholder = st.empty()
                response_text = ""
                
                try:
                    for chunk in request_model(prompt, st.session_state.model):
                        response_text += chunk
                        response_placeholder.markdown(response_text)
                    
                    if len(st.session_state.messages) > MAX_MESSAGES:
                        st.session_state.messages = []
                    
                    st.session_state.messages.append({
                        "role": "ai",
                        "content": response_text,
                        "avatar": "♟️"
                    })
                    
                except Exception as streaming_error:
                    logger.error(f"Streaming error: {streaming_error}")
                    response_placeholder.error(f"Error during response streaming: {str(streaming_error)}")
                    st.stop()
    
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        st.error(f"Failed to process your message: {str(e)}")
        st.stop()
