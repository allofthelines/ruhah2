import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

PROJECT_ID = "gen-lang-client-0869247041"
LOCATION = "asia-northeast1"  # Try this first; change to "asia-northeast1" or "europe-west1" if it fails

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Load Gemini model
model = GenerativeModel("gemini-1.5-pro-001")  # Or "gemini-1.5-pro-001"

# Generate content
response = model.generate_content(
    "Hello! Tell me a fun fact about AI.",
    generation_config=GenerationConfig(temperature=0.7)
)

print(response.text)  # Should print a generated response