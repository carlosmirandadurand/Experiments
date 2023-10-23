#%%
# Cohere Demo: Generate Endpoint using Cohere's Command Model
# Source: https://docs.cohere.com/docs/the-generate-endpoint
#         https://docs.cohere.com/docs/the-command-model
# Description: Command is Cohere’s flagship text generation model. It is trained to follow user commands and to be instantly useful in practical business applications.

import os
from dotenv import load_dotenv

import cohere


#%% 
# Connect

load_dotenv()
api_key = os.getenv('cohere_key__free_trial') 
co = cohere.Client(api_key)


#%% 
# Prompt Generative Model

my_prompt = 'Generate a social ad copy for the product: Wireless Earbuds.'

response = co.generate(
  model='command',
  prompt=my_prompt,
  max_tokens=100)

print('prompt:'        , response.generations[0].prompt)
print('text:'          , response.generations[0].text)
print('finish_reason:' , response.generations[0].finish_reason, '\n')


#%% 
# Prompt Generative Model returning likelihoods

my_prompt = 'Generate a social ad copy for the product: Wireless Earbuds.'

response = co.generate(
  model='command',
  prompt=my_prompt,
  max_tokens=100,
  return_likelihoods='GENERATION')

print('prompt:'        , response.generations[0].prompt)
print('text:'          , response.generations[0].text)
print('finish_reason:' , response.generations[0].finish_reason)
print('likelihood:'    , response.generations[0].likelihood, '\n')

for i in response.generations[0].token_likelihoods:
    print('token_likelihoods:', i.token, '\t (', i.likelihood ,')')


#%% 
# Tokenize

co.tokenize(my_prompt)


#%%
# Prompt Generative Model varying other parameters (temperature, etc.)

# Function to call the Generate endpoint
def generate_text(prompt,temperature,num_gens, model_id='command'):
  response = co.generate(
    model=model_id,
    prompt=prompt,
    temperature=temperature,
    num_generations = num_gens,
    return_likelihoods='GENERATION')
  return response

# Define the range of temperature values and num_generations
temperatures = [x / 10.0 for x in range(0, 60, 10)]
num_gens = 3

# Iterate over the range of temperature values
print(f"Temperature range: {temperatures}")
for temperature in temperatures:
  print(f'---------- Test for Temperature {temperature} ----------')
  response = generate_text(my_prompt,temperature,num_gens)
  for i in range(num_gens):
    text = response.generations[i].text
    likelihood = response.generations[i].likelihood
    print(f'Generation #{i+1}')
    print(f'Text: {text}')
    print(f'Likelihood: {likelihood}\n')



#%%
