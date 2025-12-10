# ai/advisor.py — FIXED FOR PROTOTYPE (SAFE)

import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)

# Load key from Streamlit or env
GROQ_KEY = None
try:
    GROQ_KEY = st.secrets.get("GROQ_API_KEY")
except Exception:
    GROQ_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None


print("Groq key called:", GROQ_KEY)
print("-----------------------------------------------------------------------")

# ===========================
# FALLBACK ANSWERS
# ===========================
FALLBACK_RESPONSES = {
    "emi": "EMI is the fixed monthly payment. Formula: EMI = [P*r*(1+r)^n] / ((1+r)^n - 1).",
    "credit" : "Credit score is a 3-digit score from 300-900 that decides your loan eligibility.",
    "co-applicant": "A co-applicant improves eligibility by adding income and reducing FOIR.",
    "foir": "FOIR = (All EMIs / Monthly Income) × 100. Target < 50%.",
    "default": "Hey! Mr. Finn here — ask me anything about your loan, EMI, interest rate or credit score!"
}

def get_llama_response(query, context=None):
    if client is None:
        print("CLIENT IS NONE → using fallback")
        return FALLBACK_RESPONSES.get(
            query.lower().strip(), FALLBACK_RESPONSES["default"]
        )

    try:
        print("\n🔵 SENDING REQUEST TO GROQ...")
        print("🔵 Query:", query)

        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are Mr. Finn, the loan advisor."},
                {"role": "user", "content": query}
            ],
            max_tokens=200,
            temperature=0.3
        )

        print("🟢 RAW RESPONSE:", resp)
        print("🟢 MESSAGE:", resp.choices[0].message)

        return resp.choices[0].message.content

    except Exception as e:
        print("🔴 GROQ API ERROR OCCURRED:")
        print(e)  # PRINT FULL ERROR
        print("🔴 USING FALLBACK RESPONSE")
        return FALLBACK_RESPONSES.get(
            query.lower().strip(), FALLBACK_RESPONSES["default"]
        )