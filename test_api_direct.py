"""
Direct OpenAI API test
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ API key not found")
    exit(1)

print(f"✓ API Key loaded: {api_key[:20]}...")

try:
    client = OpenAI(api_key=api_key)
    print("✓ OpenAI client initialized")
    
    print("\nAttempting simple API call...")
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, this is a test.' in one sentence."}
        ],
        temperature=0.5,
        max_tokens=50
    )
    
    print("✓ API call successful!")
    print(f"\nResponse: {response.choices[0].message.content}")
    print(f"\nModel: {response.model}")
    print(f"Tokens used: {response.usage.total_tokens}")
    
except Exception as e:
    print(f"❌ API Error: {e}")
    print(f"\nError type: {type(e).__name__}")
    
    # Show helpful guidance
    if "insufficient_quota" in str(e):
        print("\n" + "="*60)
        print("QUOTA ISSUE DETECTED")
        print("="*60)
        print("Your OpenAI account has a billing/quota issue:")
        print("1. Go to https://platform.openai.com/account/billing/overview")
        print("2. Check your usage and billing status")
        print("3. Add a payment method if needed")
        print("4. Verify the API is enabled for your account")
        print("="*60)
    elif "invalid_api_key" in str(e):
        print("\nThe API key may be revoked or incorrect.")
        print("Please check your .env file.")
