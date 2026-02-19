"""
Check available Groq models
"""
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if api_key:
    client = Groq(api_key=api_key)
    
    # List available models
    print("Available Groq Models:")
    print("=" * 60)
    
    try:
        models = client.models.list()
        for model in models.data:
            print(f"  • {model.id}")
    except Exception as e:
        print(f"Error: {e}")
        print("\nCommon Groq models to try:")
        print("  • gemma-7b-it")
        print("  • gemma2-9b-it")
        print("  • llama-3.1-70b-versatile")
        print("  • llama-3.1-8b-instant")
        print("  • mixtral-8x7b-32768")
