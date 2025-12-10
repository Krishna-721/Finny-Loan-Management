import os
from groq import Groq
# Load API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please set it before running this script.")

client = Groq(api_key=GROQ_API_KEY)

print("\n🔍 FETCHING AVAILABLE MODELS...\n")

models = client.models.list()

for m in models.data:
    print("•", m.id)
