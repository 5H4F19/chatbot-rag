# ollama_test.py
# This script checks if Ollama is running and can return a response from a local model.

import ollama
from config import OLLAMA_MODEL

try:
    response = ollama.chat(OLLAMA_MODEL, messages=[{'role': 'user', 'content': 'Hello, Ollama!'}])
    print("Ollama response:", response['message']['content'])
except Exception as e:
    print("Error communicating with Ollama:", e)
