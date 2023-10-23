#%%
# Cohere Chat Demo
# https://docs.cohere.com/docs/cochat-beta

import os
from dotenv import load_dotenv

import cohere


#%% 
# Connect

load_dotenv()
api_key = os.getenv('cohere_key__free_trial') 
co = cohere.Client(api_key)


#%% 
# First chat completion

message = "Hello World!"

response = co.chat(
	message, 
	model="command", 
	temperature=0.9
)

answer = response.text

answer


#%% 
# Chat completions with history

chat_history = [
	{"user_name": "User", "text": "Hey!"},
	{"user_name": "Chatbot", "text": "Hey! How can I help you today?"},
]
message = "Can you tell me about LLMs?"

response = co.chat(
	message=message,
	chat_history=chat_history
)

answer = response.text

answer


#%% 
# Full conversation 

chat_history = []
max_turns = 10

for _ in range(max_turns):
  # get user input
  message = input("Send the model a message: ")
  print(message)

  # generate a response with the current chat history
  response = co.chat(
    message,
    temperature=0.8,
    chat_history=chat_history
  )
  answer = response.text
    
  print(answer)
  print('-'*80)

  if message == 'Bye': 
      break

  # add message and answer to the chat history
  user_message = {"user_name": "User", "text": message}
  bot_message = {"user_name": "Chatbot", "text": answer}

  chat_history.append(user_message)
  chat_history.append(bot_message)



#%%


