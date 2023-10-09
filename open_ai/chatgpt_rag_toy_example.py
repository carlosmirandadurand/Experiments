#%%

import os
import spacy
import torch
import openai

from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from transformers import T5Tokenizer, T5ForConditionalGeneration, pipeline



#%%
# 0. Connect to Open AI

load_dotenv()
openai.organization = os.getenv('openai_organization_id')
openai.api_key      = os.getenv('openai_organization_key')


#%%
# 1. Load the medium English model from spaCy
#    Dependency: 
#       python -m spacy download en_core_web_md  
#    Alternative:
#      import en_core_web_md
#      nlp = en_core_web_md.load()

nlp = spacy.load('en_core_web_md')



#%%
# 2. Define a database of 20 sentences

database = [
    "The sky is blue.",
    "Dogs are known to be loyal animals.",
    "The capital of France is Paris.",
    "Basketball is played with a round ball.",
    "Fish breathe using gills.",
    "Computers have become an integral part of our lives.",
    "The Great Wall of China is very long.",
    "Elephants are the largest land animals.",
    "Coffee is a popular beverage worldwide.",
    "Mount Everest is the highest mountain.",
    "Roses are red.",
    "Shakespeare was a famous playwright.",
    "Penguins are flightless birds.",
    "Diamonds are one of the hardest substances.",
    "Oceans cover a large part of the Earth.",
    "Pizza is loved by many around the world.",
    "The Amazon rainforest has a rich biodiversity.",
    "Solar energy comes from the sun.",
    "Polar bears live in cold climates.",
    "Gravity is what keeps us grounded."
]

#%%
# 3. Calculate embedding vectors for each sentence and store them

database_embeddings = [nlp(sentence).vector for sentence in database]


#%%
# 4. Define a string variable named "query" with a question
query = "What is the hardest substance in the world?"


#%%
# 5. Calculate the embedding vector for the query

query_embedding = nlp(query).vector
print(query_embedding)


#%%
# 6. Calculate cosine distances: 1 - cosine_similarity 
# (we subtract the similarity from 1 to get the distance)

distances = 1 - cosine_similarity([query_embedding], database_embeddings)
print(distances)


#%%
# 7. Find the 3 sentences from the database with the smallest cosine distances to the query

top_3_indices = distances[0].argsort()[:3]
top_3_sentences = [database[index] for index in top_3_indices]

print(top_3_sentences)


#%%
# 8. Combine the retrieved sentences to form the context.

context = " ".join(top_3_sentences)


#%%
# 9. Generate a response using T5 available in Hugging Face:

# Contextualize the question:
# Assuming that the model works better with the format "question: [User's question] context: [Context]",
combined_input = f"question: {query} context: {context}"

# Initialize the model and tokenizer
MODEL_NAME = "t5-base"
tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)

# Tokenize the combined input and generate a response
input_ids = tokenizer.encode(combined_input, return_tensors="pt")
outputs = model.generate(input_ids)

# Decode the outputs to get the response text
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

print(f"Question: {query}")
print(f"Response: {response}")


#%%
# 10. Generate a response using Open AI Completion API:

# Contextualize the question:
# Here, we're forming a prompt for ChatGPT where it's provided both the user's question and the context from our top retrieved sentences.
prompt = f"Based on the following information: '{context}', answer the question: '{query}'."

# Generate a response using ChatGPT:
response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=150)

print(f"Question: {query}")
print(f"Response: {response.choices[0].text.strip()}")



#%%
# 11. Generate a response using Open AI Chat Completion API:

# Contextualize the question using a conversation structure:
messages = [
    {"role": "system", "content": "You are a helpful assistant that uses context to answer questions."},
    {"role": "user", "content": f"Based on the following information: '{context}', what is the answer to: '{query}'?"}
]

# Generate a response using ChatGPT with Chat Completion API:
response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

# Extracting the assistant's message from the response
assistant_message = response.choices[0].message['content']

print(f"Question: {query}")
print(f"Response: {assistant_message}")



#%% END
