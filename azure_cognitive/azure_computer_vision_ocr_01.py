# Azure Cognitive Services 
# Computer Vision API (v3.2) 
# SDK Example for OCR 
# 
# OCR: Read File using the Read API, extract text - remote
# This example will extract text in an image, then print results, line by line.
# This API call can also extract handwriting style text (not shown).
#
# Reference: https://learn.microsoft.com/en-us/azure/cognitive-services/Computer-vision/quickstarts-sdk/client-library?pivots=programming-language-python&tabs=visual-studio 
# Requires: pillow azure-cognitiveservices-vision-computervision


#%%
import os
import sys
import time
from dotenv import load_dotenv
from array import array
from PIL import Image

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials



#%%

# Load Azure ML parameters from environment variables
load_dotenv()

subscription_id = os.getenv('az_subscription_id')
endpoint = os.getenv('azc_cv_instance_endpoint')
subscription_key = os.getenv('azc_cv_instance_key')

# Image url to process with OCR
read_image_url = "https://raw.githubusercontent.com/MicrosoftDocs/azure-docs/master/articles/cognitive-services/Computer-vision/Images/readsample.jpg"


#%%
# Create a client
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

print("Computer Vision verion:", computervision_client.api_version)
print("Computer Vision base url:", computervision_client.config.base_url)
print("Computer Vision endpoint:", computervision_client.config.endpoint)


#%%
# Call API with URL and raw response (allows you to get the operation location)
read_response = computervision_client.read(read_image_url,  raw=True)  # Optional: model_version="2022-04-30"

print(read_response.response)
print(read_response.output)


#%%
# Get the operation location (URL with an ID at the end) from the response

read_operation_location = read_response.headers["Operation-Location"]
operation_id = read_operation_location.split("/")[-1]
print(operation_id)




#%%
# Call the "GET" API and wait for it to retrieve the results 

print("Reading results...")
while True:
    read_result = computervision_client.get_read_result(operation_id)
    if read_result.status not in ['notStarted', 'running']:
        break
    time.sleep(1)

# Print the detected text, line by line
print("Printing results...")
if read_result.status == OperationStatusCodes.succeeded:
    for text_result in read_result.analyze_result.read_results:
        for line in text_result.lines:
            print(line.text)
            print(line.bounding_box)

print("Print complete.")



#%%



