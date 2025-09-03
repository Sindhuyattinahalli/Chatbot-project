import cohere  # type: ignore
import streamlit as st  # For creating the web interface

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Medical Chatbot 🩺", layout="wide")

# ---------- UPDATED CUSTOM CSS ----------
st.markdown("""
    <style>
        /* Remove all padding and margin from the main container */
        .main {
            padding: 0;
            margin: 0;
        }
        /* Chat container with reduced top space */
        .chat-container {
            width: 100%;
            height: auto;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;  /* Ensures content starts from the top */
            padding: 1rem;
            background-color: #ffffff;
            border-radius: 10px;
            overflow-y: auto;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin-top: 0; /* Removes any top margin */
        }
        /* User message styling */
        .user-msg {
            background-color: #4e8c61;
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            max-width: 80%;
            align-self: flex-end;
            word-wrap: break-word;
            font-size: 20px;  /* Increased font size for user message */
        }
        /* Bot message styling */
        .bot-msg {
            background-color: #d1e7dd;
            color: black;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            width: 100%;  /* Make the bot answer take up full width */
            word-wrap: break-word;
            font-size: 20px;  /* Increased font size for bot message */
        }
        /* Input field without a box or container */
        .stTextInput {
            background-color: transparent;  /* Ensure the container has no background */
            border: none;  /* Remove border */
            padding: 0;  /* Remove extra padding */
            margin: 0;  /* Remove any margin */
        }
        .stTextInput input {
            background-color: transparent;  /* Remove input box background */
            border: none;  /* Remove border */
            padding: 15px;
            font-size: 20px;  /* Increased font size for input */
            width: 100%;
            box-shadow: none;  /* Remove box shadow */
            margin: 0;  /* Remove margin */
        }
        /* Styling for the submit button to keep it inline with input */
        .stButton button {
            background-color: #4f81bd;
            color: white;
            font-size: 20px;  /* Increased font size for button */
            border-radius: 6px;
            padding: 15px;
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: background-color 0.3s;
            margin-top: 10px;  /* Add margin to separate button */
        }
        .stButton button:hover {
            background-color: #355f91;
        }
        /* Remove unnecessary scrollbar space */
        .chat-container::-webkit-scrollbar {
            width: 6px;
        }
        .chat-container::-webkit-scrollbar-thumb {
            background-color: #888;
            border-radius: 10px;
        }
        .chat-container::-webkit-scrollbar-thumb:hover {
            background-color: #555;
        }
        /* Increase heading font size */
        h3 {
            font-size: 24px;  /* Increased font size for headings */
            font-weight: bold;
            color: #333;
        }
        /* Increased font size for the intro text */
        .intro-header {
            font-size: 36px;  /* Increased font size for the chatbot header */
            font-weight: bold;
            color: #333;
            text-align: center;
            margin-bottom: 10px;  /* Spacing below the header */
        }
        .intro-text {
            font-size: 26px;  /* Increased font size for the description text */
            color: #555;
            text-align: center;
            margin-bottom: 20px;  /* Spacing below the description */
        }
    </style>
""", unsafe_allow_html=True)

# ---------- COHERE INITIALIZATION ----------
try:
    co = cohere.Client("PVibIuSTwdGlHJWOV3cLFy0iCV9lzqHx9B4lp8eG")  # Add your Cohere API key here
except Exception as e:
    st.error(f"Error initializing Cohere client: {e}")
    st.stop()

# ---------- FUNCTIONS ----------

def generate_cohere_response(user_input):
    try:
        # Structure the prompt for Cohere to generate a response with four specific sections
        structured_prompt = f"""
        You are a medical chatbot. If the user's input is related to a disease or medical condition, you MUST respond in the following format:
        1) Symptoms: [List the symptoms]
        2) Treatment: [Describe treatment options]
        3) Prevention: [Explain preventive measures]
        4) Care Measures: [Specific care measures]

        User Input: {user_input}
        Response:
        """
        
        # Generate response using Cohere API
        response = co.generate(
            prompt=structured_prompt,
            max_tokens=300,
            temperature=0.7,
            k=0,
            stop_sequences=[],
            return_likelihoods='NONE'
        )
        
        generated_text = response.generations[0].text.strip()
        
        # Ensure all four sections are included, if not add a basic Care Measures section
        if any(keyword in user_input.lower() for keyword in ['disease', 'condition', 'covid', 'diabetes', 'cancer', 'flu']) and not is_complete_response(generated_text): # type: ignore
            generated_text += "\n4) Care Measures: Monitor symptoms, consult a healthcare provider 🩺, stay hydrated 💧, and rest adequately 🛏."
        
        return generated_text
    except Exception as e:
        return f"Error generating response: {e}"

# ---------- MAIN CHATBOT FUNCTION ----------

def chatbot():
    # Chatbot Header with increased font size
    st.markdown("""
    <div class="intro-header">
        Medical Chatbot 🤖
    </div>
    <div class="intro-text">
        Your health matters ❤. Ask me anything about medical conditions, and I'll guide you with clear, caring, and expert-backed answers 🩺.
    </div>
    """, unsafe_allow_html=True)

    # Conversation History
    if 'history' not in st.session_state:
        st.session_state.history = []

    # User Input
    user_input = st.text_input("Ask your question:", "")

    if user_input:
        # Add user message to the history
        st.session_state.history.append(f"Ask your question: {user_input}")

        # Generate response using Cohere
        response = generate_cohere_response(user_input)

        # Add bot response to the history
        st.session_state.history.append(f"Bot: {response}")

    # Display Conversation History
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        for message in st.session_state.history:
            if message.startswith("Ask your question:"):
                st.markdown(f'<div class="user-msg">{message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-msg">{message}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# ---------- RUNNING THE CHATBOT ----------
if __name__ == "__main__":
    chatbot()