import streamlit as st
from groq import Groq

# Streamlit Cloud loads API keys ONLY through st.secrets
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_KEY = None

client = None
if GROQ_KEY:
    client = Groq(api_key=GROQ_KEY)


# -----------------------------------------------------------
# Build context-aware system prompt
# -----------------------------------------------------------
def build_context_prompt(context):
    loan_amt = context.get("loan_amount", 0)
    tenure = context.get("tenure", 0)
    rate = context.get("rate", 0)
    income = context.get("income", 0)

    return f"""
    You are **Mr. Finn — an intelligent loan advisor for LoanFlow Banking.**
    You should talk like a real human financial advisor, using a friendly and professional tone.

    For every user interaction, always start responses with :
    "Hey! Mr. Finn here, your personal loan advisor"

    Your role:
    - Answer ONLY banking, loans, credit score, EMI, interest, documentation, or underwriting questions.
    - If asked anything outside banking, politely decline and redirect.

    Communication rules:
    - Explain clearly and use bullet points whenever needed and helpful.
    - Stay concise (max ~200 words).
    - Maintain a professional, empathetic tone.
    - Never give legally binding advice.

    Banking rules to follow:
    - Use real Indian norms: FOIR, DTI, CIBIL score bands, basic risk-based pricing.
    - Mention that interest rates vary by bank and market conditions.
    - Do NOT hallucinate RBI rules, bank policies, or fees.

    Context usage:
    - If loan context is available, use it:
    • Loan Amount: ₹{loan_amt:,}
    • Tenure: {tenure} months
    • Interest Rate: {rate}%
    • Annual Income: ₹{income:,}

    - If context is missing, give general Indian examples.

    Safety rules:
    - Never fabricate numbers or policies.
    - If unsure or missing details, ask:
    “Would you like me to connect you with customer care?”

""" 


# -----------------------------------------------------------
# Call Groq LLaMA 3.2 — primary AI engine
# -----------------------------------------------------------
def call_groq_llama(prompt):
    if client is None:
        return None  # No API key

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are FINN, Loan Advisor AI."},
                      {"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=350
        )
        return response.choices[0].message.content

    except Exception as e:
        print("Groq error:", e)
        return None


# -----------------------------------------------------------
# Main function used by app.py
# -----------------------------------------------------------
def get_llama_response(user_question, context):
    prompt = build_context_prompt(context) + f"\n\nUser Question: {user_question}\nAnswer:"

    # 1) Try Groq first
    ai_text = call_groq_llama(prompt)

    if ai_text:
        return ai_text, "groq-llama"

    # 2) Fallback if Groq unavailable
    fallback = (
        "⚠️ I'm unable to reach the AI engine right now.\n"
        "Would you like me to connect you with customer care?"
    )
    return fallback, "fallback"
