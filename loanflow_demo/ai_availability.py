from groq import Groq
GROQ_API_KEY= ""
client = Groq(api_key=GROQ_API_KEY)

print("\n🔍 FETCHING AVAILABLE MODELS...\n")

models = client.models.list()

for m in models.data:
    print("•", m.id)
