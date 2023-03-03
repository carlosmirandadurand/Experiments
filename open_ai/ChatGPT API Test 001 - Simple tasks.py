#%%
import os
import json
import time
import textwrap
import requests

from dotenv import load_dotenv


#%%
# Load environment variables

load_dotenv()
openai_organization_id = os.getenv('openai_organization_id')
openai_organization_key = os.getenv('openai_organization_key')


#%%
# Load process parameters

model = 'gpt-3.5-turbo'
endpoint = 'v1/chat/completions'
temperature = 0

prompt = 'It is 9:00pm. You just saw me. Greet me in Spanish, formally.'
print(prompt)


#%%
# Prepare the API call

url = f"https://api.openai.com/{endpoint}"

headers = {'Content-Type': 'application/json', 
           'Authorization': f'Bearer {openai_organization_key}'
           }

json_payload = {
  "model": model,
  "messages": [{"role": "user", "content": prompt}]
}

print(url)
print(headers)
print(json_payload)


#%%
# Execute the API call

response = requests.post(url, json=json_payload, headers=headers)
response

#%%
# Parse the response

print('Model employed:', response.json()['model'])
print('Tokens used:', response.json()['usage'])

for answer in response.json()['choices']:
    print(answer['message']['role'], ":", answer['message']['content'].strip() )



#%%
# To call the API via CURL (not recommended)

# curl https://api.openai.com/v1/chat/completions 
# -H 'Content-Type: application/json' 
# -H 'Authorization: Bearer %s' 
# -d '{ 
# "model": "gpt-3.5-turbo", 
# "messages": [{"role": "user", "content": "Hello!"}] 
# }'  
#
# curl_command = textwrap.dedent(curl_command).strip()
# print(curl_command)
#
# curl_response = json.loads(os.popen(curl_command).read())
# curl_response

