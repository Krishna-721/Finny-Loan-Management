# ai/groq_client.py

import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)

# Load key from Streamlit secrets or env
GROQ_KEY = None
try:
    GROQ_KEY = st.secrets.get("GROQ_API_KEY")
except Exception:
    GROQ_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

# Fallback responses if API fails
FALLBACK_RESPONSES = {
    "greeting": "Welcome to LoanFlow AI! I'm Mr. Finn, Your Loan Agent. Would you like to apply for a personal loan?",
    "pan": "To check your eligibility, I'll need your PAN number. Could you share it? (Format: ABCDE1234F)",
    "default": "I'm here to help with your loan application. What would you like to know?"
}

def get_llama_response(prompt, max_tokens=250, temperature=0.4):
    """
    Get response from Groq Llama model with fallback
    """
    if client is None:
        print("⚠️ Groq client not initialized - using fallback")
        return FALLBACK_RESPONSES["default"]
    
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are Agent Finn, a professional loan advisor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return resp.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"🔴 Groq API Error: {e}")
        return FALLBACK_RESPONSES["default"]