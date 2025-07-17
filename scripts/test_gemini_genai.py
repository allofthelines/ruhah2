import google.generativeai as genai

# Your API key (ensure it's correct from the Gemini API project)
API_KEY = "AIzaSyABrLYaoB4yDJdDEKBjwmJ3PYsi17Wkhks"  # Replace if needed

genai.configure(api_key=API_KEY)

# List all available models and their methods
for model in genai.list_models():
    print(f"Model: {model.name}")
    print(f"Supported Methods: {model.supported_generation_methods}")
    print("---")