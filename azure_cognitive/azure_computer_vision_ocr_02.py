# Azure Cognitive Services 
# Computer Vision API (v3.2) 
# REST API Example for OCR 
# 
# Quickstart: Extract printed and handwritten text using the Computer Vision REST API and Python
# Reference: https://github.com/Azure-Samples/cognitive-services-quickstart-code/blob/master/python/ComputerVision/REST/python-hand-text.md
# Additional example: https://github.com/microsoft/Cognitive-Vision-Python/blob/master/Jupyter%20Notebook/Handwriting%20OCR%20API%20Example.ipynb  (TODO: Run it)


#%%
import os
import sys
import json
import requests
import time
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

# If you are using a Jupyter Notebook, uncomment the following line.
# %matplotlib inline
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


#%%
# Load parameters from environment variables

load_dotenv()
subscription_id = os.getenv('az_subscription_id')
endpoint = os.getenv('azc_cv_instance_endpoint')
subscription_key = os.getenv('azc_cv_instance_key')


#%%
# Configure source image and other process parameters

img_url = "https://github.com/microsoft/Cognitive-Vision-Python/blob/master/Jupyter%20Notebook/Z.jpg?raw=true"

# Few test examples. Pick one:
# img_url = "https://raw.githubusercontent.com/MicrosoftDocs/azure-docs/master/articles/cognitive-services/Computer-vision/Images/readsample.jpg"
# img_url = "https://www.shaip.com/wp-content/uploads/2020/10/Invoice-Data-Collection.jpg"
# img_url = "https://github.com/microsoft/Cognitive-Vision-Python/blob/master/Jupyter%20Notebook/Z.jpg?raw=true"
# TODO: Change process to feed local file, e.g. "/home/carlosm/Pictures/Images_for_OCR/readsample_downloaded.jpg"


#%%
# Extracting text requires two API calls: 
# 1. Submit the image for processing
# 2. Retrieve the text found in the image
#
# Submit HTTP request to process image

text_recognition_url = endpoint + "/vision/v3.1/read/analyze"

headers = {'Ocp-Apim-Subscription-Key': subscription_key}

data = {'url': img_url}

response = requests.post(
    text_recognition_url, 
    headers=headers, 
    json=data)

response.raise_for_status()


#%%
# Submit HTTP request to get text from the image
# Poll server until results are avalable 

ocr_text_lines = {}

while True:
    response_final = requests.get(
        response.headers["Operation-Location"], 
        headers=headers)
    ocr_text_lines = response_final.json()
    
    print(json.dumps(ocr_text_lines, indent=4))

    time.sleep(1)

    if ("analyzeResult" in ocr_text_lines):
        break

    if ("status" in ocr_text_lines and ocr_text_lines['status'] == 'failed'):
        break


#%%
# Extract the recognized text, with bounding boxes.

polygons = []
if ("analyzeResult" in ocr_text_lines):
    polygons = [(line["boundingBox"], line["text"])
                for line in ocr_text_lines["analyzeResult"]["readResults"][0]["lines"]]


#%%
# Display the image and overlay it with the extracted text

image = Image.open(BytesIO(requests.get(img_url).content))
ax = plt.imshow(image)
for polygon in polygons:
    vertices = [(polygon[0][i], polygon[0][i+1])
                for i in range(0, len(polygon[0]), 2)]
    text = polygon[1]
    patch = Polygon(vertices, closed=True, fill=False, linewidth=2, color='y')
    ax.axes.add_patch(patch)
    plt.text(vertices[0][0], vertices[0][1], text, fontsize=20, va="top")
plt.show()

print("End")


#%%

