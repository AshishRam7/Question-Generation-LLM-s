import os
import openai

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_embedding(text, model="text-embedding-3-large"):
    """
    Generate an embedding for the given text using the specified model.
    """
    # Clean up the input text
    text = text.replace("\n", " ")
    
    # Request the embedding from OpenAI
    response = openai.Embedding.create(input=[text], model=model)
    
    # Extract and return the embedding from the response
    embedding = response["data"][0]["embedding"]
    return embedding

# Sample sentence to embed
sample_text = "This article is about new OpenAI Embeddings."

# Get the embedding for the sample sentence
embedding = get_embedding(sample_text)

# Print the resulting embedding
print("Embedding for the sample sentence:")
print(embedding)
