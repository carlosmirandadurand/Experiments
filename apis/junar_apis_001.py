# Junar APIs
# https://junar.github.io/docs/es/index.html


#%%
import os
import json
import time
import requests
from dotenv import load_dotenv

#%%
# Load process parameters from environment

load_dotenv()



#%%
# Define helper functions

def junarURL (action='resources', 
              item=None, 
              base=None, 
              key=None, 
              formato="json", 
              limit=None, 
              offset=None, 
              order=None, 
              query=None, 
              categories=[], 
              resources=[]):

    if not(base):
        base = os.getenv('junar_api_base_url')
    if not(key):
        key = os.getenv('junar_api_key')

    if item:
        url = f"{base}/api/v2/{action}/{item}/data.{formato}/?auth_key={key}"
    else:
        url = f"{base}/api/v2/{action}.{formato}/?auth_key={key}"

    if limit:
        url = f'{url}&limit={limit}'
    if offset:
        url = f'{url}&offset={offset}'
    if query:
        url = f'{url}&query={query}'
    if order:
        url = f'{url}&order={order}'
    if categories:
        categories_str = ','.join(map(str, categories)) 
        url = f'{url}&query={categories_str}'
    if resources:
        resources_str = ','.join(map(str, resources)) 
        url = f'{url}&query={resources_str}'
        
    return url


#%%
# Prepare output folder

output_base_directory = os.getcwd()
output_subdirectory = 'downloads'
output_directory = os.path.join(output_base_directory, output_subdirectory)

try:
    os.makedirs(output_directory)
    print(f"Created directory: {output_directory}")
except FileExistsError:
    print(f"Directory already exists: {output_directory}")


#%%
# Execute

output_file_name = 'request_001.json'

request = junarURL()
response = requests.get(request).json()
time.sleep(1) 

with open(os.path.join(output_directory, output_file_name), 'w') as f:
    json.dump(response, f)




#%%
# End. The rest are snippets for possible future use.

# def processRequest(url, json, data, headers, params, max_retries = 10):
#     """
#     Helper function to process the request 
#
#     Parameters:
#     json: Used when processing images from its URL. See API Documentation
#     data: Used when processing image read from disk. See API Documentation
#     headers: Used to pass the key information and the data type request
#     """
#  
#     retries = 0
#     result = None
#
#     while True:
#
#         response = requests.request( 'post', url, json = json, data = data, headers = headers, params = params )
#
#         if response.status_code == 429: 
#
#             print( "Message: %s" % ( response.json() ) )
#
#             if retries <= max_retries: 
#                 time.sleep(1) 
#                 retries += 1
#                 continue
#             else: 
#                 print( 'Error: failed after retrying!' )
#                 break
#
#         elif response.status_code == 200 or response.status_code == 201:
#
#             if 'content-length' in response.headers and int(response.headers['content-length']) == 0: 
#                 result = None 
#             elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str): 
#                 if 'application/json' in response.headers['content-type'].lower(): 
#                     result = response.json() if response.content else None 
#                 elif 'image' in response.headers['content-type'].lower(): 
#                     result = response.content
#         else:
#             print( "Error code: %d" % ( response.status_code ) )
#             print( "Message: %s" % ( response.json() ) )
#
#         break
#        
#     return result

# response = requests.get('https://api.covid19api.com/summary').text
# response_info = json.loads(response)
# response_info

# response_info = requests.get(‘https://api.covid19api.com/summary’).json()
# response_info
