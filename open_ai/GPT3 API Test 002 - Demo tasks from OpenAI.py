#%%
import os
import time
import openai
import textwrap

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()


#%%
# Connect to OpenAI and load the list of models

openai.organization = os.getenv('openai_organization_id')
openai.api_key = os.getenv('openai_organization_key')

openai_model_list = openai.Model.list()
openai_model_ids  = sorted([ i["id"] for i in openai_model_list['data']])
print('List of Models:\n -', '\n - '.join(openai_model_ids), '\n')


#%%
# Pick the model to use 

model = 'text-davinci-003'



#%%
# Load input prompts
# Examples from https://openai.com/product for: Copywriting, Summarization, Parsing text, Classification, Translation

prompt_list = [


    """
    Create promo copy for the FamilyTime mobile application. 
    It allows unlimited uploading, special filters and makes it easy to create albums of photos and videos. 
    It runs on iOS and Android""", 


    """
    Summarize this email into a single sentence:
    Dear Olivia,

    The solar energy conference went great. New Horizon Manufacturing wants to meet with us to talk about our photovoltaic window system we’re about to launch.
    I think it would be great to talk this Tuesday.

    Best,
    Allison
    """,


    """
    Answer the following questions about this customer email:

    I’m wondering if you could provide me with information about your cloud services for companies. I’m CTO for Moon Door, a movie production company and want to know if it can help us manage our different projects that are in production.

    Questions:
    1. What industry is the company
    2. What is the name of the company
    3. What are they interested in
    4. What is the customer’s position
    """,


    """
    Choose a genre category (“fiction”, “young adult”, “science fiction”, “fantasy”, “other”) for each book: 
    1. The Hunger Games, 
    2. The Kite Runner 
    3. A Wrinkle in Time 
    and make a list of the book and its genre:
    """,


    """Translate this into Spanish: Where can I find a bookstore?""",

]

# Cleanup spacing     
prompt_list = [textwrap.dedent(i) for i in prompt_list]


#%%
# Test GPT-3

for prompt in prompt_list:

    print(f'Prompt: {prompt}\n')

    completion = openai.Completion.create(
        engine = model,
        prompt = prompt,
        max_tokens = 2000,
        n = 3,
        stop = None,
        temperature = 0.5,
        user = "CMD1"
    )

    for response in completion.choices:
        print(f'Response { response.index + 1 }: { response.text.lstrip() }\n\n')

    print('-' * 80)

    time.sleep(3) 


# %%
