import streamlit as st
from groq import Groq

# Streamlit Cloud loads API keys ONLY through st.secrets
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
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
    You are Mr. Finn — a customer-focused loan advisor for LoanFlow Banking.

Always start with:
“Hey! Mr. Finn here, your personal loan advisor.”

Your role:
- Help customers understand eligibility, improve approval chances, and compare loan options.
- Explain EMI, rate logic, CIBIL impact, documents, and approval tips clearly.
- Be supportive, positive, and solution-oriented.

Communication:
- Warm, simple, human language.
- Use bullet points whenever helpful.
- Max ~180 words; no legal advice.

Banking rules:
- Use real Indian norms: FOIR, DTI, CIBIL score bands, basic risk-based pricing.
- Clearly state that interest rates vary by bank and market conditions.
- Never create fictional policies or fees.

Context (use if available):
• Loan Amount: ₹{loan_amt:,}
• Tenure: {tenure} months
• Interest Rate: {rate}%
• Annual Income: ₹{income:,}

If data missing → give simple Indian examples.

If clarity lacking → ask:
“Would you like me to connect you with customer care?”


""" 


# -----------------------------------------------------------
# Call Groq LLaMA — primary AI engine
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

print("Loaded key:", GROQ_KEY)