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
from itertools import cycle 

import cv2
import urllib.request
import numpy as np

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials



#%%
# Load parameters from environment variables

load_dotenv()
subscription_id = os.getenv('az_subscription_id')
endpoint = os.getenv('azc_cv_instance_endpoint')
subscription_key = os.getenv('azc_cv_instance_key')


#%%
# Configure source image and other process parameters

img_url = "https://raw.githubusercontent.com/MicrosoftDocs/azure-docs/master/articles/cognitive-services/Computer-vision/Images/readsample.jpg"
img_scale_percent = 50   # 25, 50, 75, 100, 150, 200
img_print_text = True    # True / False
bbox_color_cycle = cycle([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 255), ]) # BGR

# Few test examples. Pick one:
# img_url = "https://raw.githubusercontent.com/MicrosoftDocs/azure-docs/master/articles/cognitive-services/Computer-vision/Images/readsample.jpg"
# img_url = "https://www.shaip.com/wp-content/uploads/2020/10/Invoice-Data-Collection.jpg"
# TODO: Change process to feed local file, e.g. "/home/carlosm/Pictures/Images_for_OCR/readsample_downloaded.jpg"



#%%
# Azure CV OCR: Create a client
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

print("Computer Vision verion:", computervision_client.api_version)
print("Computer Vision base url:", computervision_client.config.base_url)
print("Computer Vision endpoint:", computervision_client.config.endpoint)


#%%
# Azure CV OCR: Call API with URL and raw response (allows you to get the operation location)
read_response = computervision_client.read(img_url,  raw=True)  # Optional: model_version="2022-04-30"

print(read_response.response)
print(read_response.output)


#%%
# Azure CV OCR: Get the operation location (URL with an ID at the end) from the response

read_operation_location = read_response.headers["Operation-Location"]
operation_id = read_operation_location.split("/")[-1]
print(operation_id)


#%%
# Azure CV OCR: Call the "GET" API and wait for it to retrieve the results 

print("Reading OCR results...")
while True:
    read_result = computervision_client.get_read_result(operation_id)
    if read_result.status not in ['notStarted', 'running']:
        break
    time.sleep(1)

list_ocr_results  = []
if read_result.status == OperationStatusCodes.succeeded:
    for text_result in read_result.analyze_result.read_results:
        for line in text_result.lines:
            list_ocr_results.append ({'text': line.text, 'bbox': line.bounding_box} )

for r in list_ocr_results: 
    print(f"{r['text']} \nBB:{r['bbox']}")

print("OCR complete!")


#%%
# Validation of the OCR: Load image from URL

with urllib.request.urlopen(img_url) as req:
    img_arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    img = cv2.imdecode(img_arr, -1) 


#%%
# Validation of the OCR: Add the bounding boxes and text 

for r in list_ocr_results: 
    print(f"{r['text']} \nBB:{r['bbox']}\n")
    x1, y1, x2, y2, x3, y3, x4, y4 = r['bbox']
    img_color = next(bbox_color_cycle)
    img_pts = np.array(
        [[x1, y1], 
        [x2, y2],
        [x3, y3], 
        [x4, y4]],
        np.int32)
    img = cv2.polylines(
        img, 
        [img_pts],
        isClosed = True, 
        color = img_color,
        thickness = 2) 
    if img_print_text:
        img = cv2.putText(
            img, 
            r['text'], 
            (int(x1), int(y1)), 
            fontFace = cv2.FONT_HERSHEY_SIMPLEX, 
            fontScale = 1, 
            color = img_color,
            thickness = 2, 
            lineType = cv2.LINE_AA)
  
# cv2.imwrite("img_with_bounding_boxes.jpg", img)


#%%
# Validation of the OCR: Rezize and show the image

img_width  = int(img.shape[1] * img_scale_percent / 100)
img_height = int(img.shape[0] * img_scale_percent / 100)
img_resized = cv2.resize(img, (img_width, img_height), interpolation = cv2.INTER_AREA)
 
print("Displaying image")
print('Original Dimensions : ',img.shape)
print('Resized Dimensions  : ',img_resized.shape)
print("Click any key to continue...")

cv2.imshow('Downloaded Image (click any key to continue)', img_resized)
cv2.waitKey()
cv2.destroyAllWindows()

print("End")


#%%

