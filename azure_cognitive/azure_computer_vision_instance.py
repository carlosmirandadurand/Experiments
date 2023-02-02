# Azure Cognitive Services 
# Computer Vision API (v3.2) 
# REST API Example for Image Analysis 
#
# References: 
# - https://github.com/microsoft/Cognitive-Vision-Python/blob/master/Jupyter%20Notebook/Computer%20Vision%20API%20Example.ipynb
# - https://learn.microsoft.com/en-us/azure/cognitive-services/computer-vision/quickstarts-sdk/image-analysis-client-library?tabs=visual-studio%2C3-2&pivots=programming-language-rest-api
#
# Modifications: 
# - Ported github code to Python 3
# - Ported github code to Micrsoft Computer Vision API v3.2
# - Added annotations for objects, tags, and other entity types in the image 
# - Added bounding boxes for the objects in the image 
# - Picked the category with largest confidence (reversed sort order)
# - Additional helper functions and other enhancements 
# - TODO: Test Python SDK: for example: computervision_client.tag_image(remote_image_url) function from the quick start article.


#%%

import os
import time 
import requests
import cv2
import operator
import numpy as np

from dotenv import load_dotenv
from itertools import cycle 

import matplotlib.pyplot as plt
#%matplotlib inline 


#%%
# Load parameters from environment variables

load_dotenv()
subscription_id = os.getenv('az_subscription_id')
endpoint = os.getenv('azc_cv_instance_endpoint')
subscription_key = os.getenv('azc_cv_instance_key')


#%%
# Helper Functions

def processRequest(url, json, data, headers, params, max_retries = 10):
    """
    Helper function to process the request 

    Parameters:
    json: Used when processing images from its URL. See API Documentation
    data: Used when processing image read from disk. See API Documentation
    headers: Used to pass the key information and the data type request
    """
  
    retries = 0
    result = None

    while True:

        response = requests.request( 'post', url, json = json, data = data, headers = headers, params = params )

        if response.status_code == 429: 

            print( "Message: %s" % ( response.json() ) )

            if retries <= max_retries: 
                time.sleep(1) 
                retries += 1
                continue
            else: 
                print( 'Error: failed after retrying!' )
                break

        elif response.status_code == 200 or response.status_code == 201:

            if 'content-length' in response.headers and int(response.headers['content-length']) == 0: 
                result = None 
            elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str): 
                if 'application/json' in response.headers['content-type'].lower(): 
                    result = response.json() if response.content else None 
                elif 'image' in response.headers['content-type'].lower(): 
                    result = response.content
        else:
            print( "Error code: %d" % ( response.status_code ) )
            print( "Message: %s" % ( response.json() ) )

        break
        
    return result


def renderResultOnImage( result, img ):
    
    """Display the obtained results onto the input image"""

    #bbox_color_cycle = cycle([(0, 0, 0)])
    bbox_color_cycle = cycle([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255),]) # BGR
    title = ""

    if 'color' in result and len(result['color']) > 0:
        R = int(result['color']['accentColor'][:2],16)
        G = int(result['color']['accentColor'][2:4],16)
        B = int(result['color']['accentColor'][4:],16)
        img = cv2.rectangle( img,(0,0), (img.shape[1], img.shape[0]), color = (R,G,B), thickness = 25 )

    if 'description' in result and len(result['description']) > 0:
        imageDescription = result['description']['captions'][0]['text']
        title = f"{title}{imageDescription}\n"
        
    if 'categories' in result and len(result['categories']) > 0:
        categoryList = sorted(result['categories'], key=lambda x:-x['score'])
        categoryName = categoryList[0]['name']
        title = f"{title}Category: {categoryName}\n"
        
    if 'tags' in result and len(result['tags']) > 0:
        title = f"{title}Tags: "
        tagList  = sorted(result['tags'], key=lambda x:-x['confidence'])
        for i in tagList:
            title = f"{title}{i['name']}({int(100*i['confidence'])}%); "
        title = f"{title}\n"
        
    if 'adult' in result and len(result['adult']) > 0:
        adultMark = 'YES' if result['adult']['isAdultContent'] else 'N'
        title = f"{title}Adult: {adultMark}\n"
    
    if 'objects' in result:
        title = f"{title}Objects: {len(result['objects'])}\n"
        for i in result['objects']:
            if 'rectangle' in i:
                img_pt1 = (i['rectangle']['x'], i['rectangle']['y'])
                img_pt2 = (i['rectangle']['x'] + i['rectangle']['w'],  
                           i['rectangle']['y'] + i['rectangle']['h'])
                img_pt3 = (i['rectangle']['x'],  
                           i['rectangle']['y'] + i['rectangle']['h'] - 5)
                img_col = next(bbox_color_cycle)
                img = cv2.rectangle(
                    img, 
                    img_pt1, 
                    img_pt2, 
                    color = (0,0,0), 
                    thickness = 3)
                img = cv2.rectangle(
                    img, 
                    img_pt1, 
                    img_pt2, 
                    color = img_col, 
                    thickness = 2)
                img = cv2.putText(
                    img, 
                    f"{i['object']}({int(100*i['confidence'])}%)", 
                    img_pt3, 
                    fontFace = cv2.FONT_HERSHEY_SIMPLEX, 
                    fontScale = 0.6, 
                    color = img_col,
                    thickness = 1, 
                    lineType = cv2.LINE_AA)
        
    tx, ty = 25, 25
    for i in title.split('\n'):
        if len(i) > 0:
            ts, _ = cv2.getTextSize(i, 
                        fontFace = cv2.FONT_HERSHEY_SIMPLEX, 
                        fontScale = 0.5, 
                        thickness = 1)
            tw, th = ts
            cv2.rectangle(img, (tx-1,ty-th-1), (tx+tw+1,int(ty+0.3*th+1)), (0,0,0), -1)
            img = cv2.putText(img, i, (tx,ty), 
                        fontFace = cv2.FONT_HERSHEY_SIMPLEX, 
                        fontScale = 0.5, 
                        color = (255,255,255), 
                        thickness = 1)
            ty += int(1.3*th + 2)
    
    return img


def printResultsOnConsole (results):

    if result is not None:
        for i in result.items():
            if not isinstance(i, tuple):
                print(f"Item {i}\n")
            elif len(i) != 2:
                print(f"TUPLE {i}:")
            elif isinstance(i[1], list):
                print(f"LIST {i[0]}:")
                for j in i[1]: print(f"   - {j}")
                print("\n")
            elif isinstance(i[1], dict):
                print(f"DICT {i[0]}:")
                for j in i[1].keys(): print(f"   - {j} = {i[1][j]}")
                print("\n")
            else:
                print(f"{i[0]}:  {i[1]}\n")
    else:
        print("No results!")



#%%##############################################################################################################################################
# Analysis of image retrieved via URL: 
# Configure source and process parameters

image_url_list = [
    "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/landmark.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Salto_del_Angel-Canaima-Venezuela08.JPG/800px-Salto_del_Angel-Canaima-Venezuela08.JPG",
    "https://scontent-dfw5-1.xx.fbcdn.net/v/t1.18169-9/27940_1485263528965_2940000_n.jpg?_nc_cat=109&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=xEAT5Pz4vJYAX8lcHtu&_nc_ht=scontent-dfw5-1.xx&oh=00_AfBl_TSalpUebLaSGCppCaR1HXHPbWBbgVymS2HpO-6bqA&oe=6402640B",
    "https://scontent-dfw5-1.xx.fbcdn.net/v/t31.18172-8/11036218_10152553256544649_1669290416624193002_o.jpg?_nc_cat=103&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=SEnbEOytxJMAX8aMiOs&_nc_ht=scontent-dfw5-1.xx&oh=00_AfCt8KbALDmItK_4D7CcBslqx5-_enV0PWxICkyx-SV3LQ&oe=64027AB5",
    "https://scontent-dfw5-2.xx.fbcdn.net/v/t31.18172-8/11393663_10152553256994649_7953012642473560880_o.jpg?_nc_cat=102&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=E9Ne4eUZiaYAX9Bg9Zn&_nc_ht=scontent-dfw5-2.xx&oh=00_AfCpxDwE1PkWUafM8MSq8fZCxRUFww0AF8jnEk92YtAOWg&oe=64026D72",
    "https://scontent-dfw5-2.xx.fbcdn.net/v/t31.18172-8/18216809_10154826961113089_29713761595749634_o.jpg?_nc_cat=106&ccb=1-7&_nc_sid=730e14&_nc_ohc=CvxqxwShyOEAX-ZEljV&tn=O_5A8de8BLeYPTjf&_nc_ht=scontent-dfw5-2.xx&oh=00_AfAWfP6PwdaEARmYuNtvKiMy82tSwe-CAHRPiYXbc19IOA&oe=64028479",
    "https://scontent-dfw5-2.xx.fbcdn.net/v/t1.18169-9/27940_1485278129330_223238_n.jpg?_nc_cat=100&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=avLAdyULaR4AX83vcej&_nc_ht=scontent-dfw5-2.xx&oh=00_AfC29NG2T0bYVLhGB8vDEZ3guznVvAeCZicRcoB3cn03GA&oe=6402955B",
    "https://scontent-dfw5-1.xx.fbcdn.net/v/t1.18169-9/27940_1485263168956_3741064_n.jpg?_nc_cat=110&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=TB54oa4fM-sAX_ilEkz&_nc_ht=scontent-dfw5-1.xx&oh=00_AfDGAiaD_rVDjDOvqV1Rez0Mr3GPq0HMHKUIU7AijLJU3w&oe=6402888C",
    "https://scontent-dfw5-2.xx.fbcdn.net/v/t1.18169-9/27940_1485263248958_2049580_n.jpg?_nc_cat=108&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=SscbopjIYGkAX9AX343&_nc_ht=scontent-dfw5-2.xx&oh=00_AfBTBJ0qB0cex9Tt7Qx8Bm-J5YEql49TDvogCGuZAV7oVg&oe=64026296",
    "https://scontent-dfw5-2.xx.fbcdn.net/v/t1.18169-9/30784_1450572621714_4401613_n.jpg?_nc_cat=106&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=wHVOVFXFiQ4AX-8hTtJ&_nc_ht=scontent-dfw5-2.xx&oh=00_AfDywUYIvKrMVbojEieohfi-7iSxWcTmvGY82Jx-plhXbA&oe=640293D3",
    "https://scontent-dfw5-2.xx.fbcdn.net/v/t1.18169-9/30784_1450572541712_1785238_n.jpg?_nc_cat=100&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=Ul8Ty8hqCHoAX8HrYyj&_nc_ht=scontent-dfw5-2.xx&oh=00_AfA-Athp-a7cTxwOXL8ESDgHGgr1bYAIklKBQfB92uqhSw&oe=6402816F",
    "https://scontent-dfw5-1.xx.fbcdn.net/v/t1.18169-9/29640_1462158391351_2289074_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=c7CIExTAnEAAX9JEbd1&_nc_ht=scontent-dfw5-1.xx&oh=00_AfAfrvb71rO6h5ae8GLcZ61ZUrjSfsV2VUh-Sgj61M-s-A&oe=640291C6",
    "https://scontent-dfw5-2.xx.fbcdn.net/v/t1.18169-9/29390_1468507710080_4297208_n.jpg?_nc_cat=107&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=fM4fSfhaEaAAX--CdRy&_nc_ht=scontent-dfw5-2.xx&oh=00_AfD_QRvtu0IEhkDRVo0ao0OTYdYgmE3ySxFOnB21mo4dZQ&oe=640276F9",
    "https://scontent-dfw5-2.xx.fbcdn.net/v/t1.18169-9/27940_1485262768946_575173_n.jpg?_nc_cat=100&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=WnorXVDh-N8AX9NKTNV&_nc_ht=scontent-dfw5-2.xx&oh=00_AfB0vSW2__ZuS2ZI8vGRMYzNLJY91hkHxEEVXedmDyidbg&oe=64027FE4",
    "https://scontent-dfw5-2.xx.fbcdn.net/v/t1.18169-9/16266022_10211320800753176_890407081294942863_n.jpg?_nc_cat=104&ccb=1-7&_nc_sid=8bfeb9&_nc_ohc=FF_c3NYLY78AX_aqHHk&_nc_ht=scontent-dfw5-2.xx&oh=00_AfAkscl9c2o2-y7RCPDwwjaKSjpT0nkDqYxm3nhgHy5eJg&oe=640289D2",
    "https://scontent-dfw5-1.xx.fbcdn.net/v/t1.18169-9/16265176_10211320801953206_4437705223098996367_n.jpg?_nc_cat=109&ccb=1-7&_nc_sid=8bfeb9&_nc_ohc=kc5kXcMjVBwAX9Pz8nL&_nc_ht=scontent-dfw5-1.xx&oh=00_AfASzb9tmeFCQ6ELiVPzK9dUYffLwn3xQVBPmZGkdHhRgw&oe=640269E0",
    "https://scontent-dfw5-2.xx.fbcdn.net/v/t1.18169-9/27940_1485264368986_520926_n.jpg?_nc_cat=108&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=MGUBhngTvykAX86Wsau&_nc_ht=scontent-dfw5-2.xx&oh=00_AfC9EDwaxlxQ4dCTC_DwIUfLR23hjaD2tTgB219y55Iz6w&oe=6402942E",
    "https://scontent-dfw5-1.xx.fbcdn.net/v/t1.18169-9/24578_1437130965681_1421542_n.jpg?_nc_cat=101&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=kYB58_EJ3pUAX9TxO_b&_nc_ht=scontent-dfw5-1.xx&oh=00_AfAUP7LwgY8bclBnBTbfJoAeh4vIVgBwW743tRWp4REGSA&oe=64028689",
    "https://scontent-dfw5-1.xx.fbcdn.net/v/t1.18169-9/24578_1437132365716_3461090_n.jpg?_nc_cat=105&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=s_KVQj-AVyAAX9SO1CS&_nc_oc=AQmwJMOz295Uu6bjYxeXTVv5Ke359dK0rZIqX39ekPQqpSZUnetA7Ttd0Res_KDvqu66jfiSr98HEi7S8lri2j4x&_nc_ht=scontent-dfw5-1.xx&oh=00_AfAAjJOYmRfU4s8BpuU4JhtMUFzOny8TJoLvo8g_ymmWkQ&oe=64028B33",
    "https://scontent-dfw5-1.xx.fbcdn.net/v/t1.18169-9/24578_1437130925680_32931_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=RsJQFoU7LTwAX_MZJBb&_nc_ht=scontent-dfw5-1.xx&oh=00_AfBmGj_t6IzHcZg1jt6wRuDlvjbQ63_2Nw0fuKom1FdRWw&oe=64027AB4",
    "https://scontent-dfw5-1.xx.fbcdn.net/v/t1.18169-9/24578_1437126605572_2400737_n.jpg?_nc_cat=111&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=cPsZRa2c6KwAX8j-0kP&tn=O_5A8de8BLeYPTjf&_nc_ht=scontent-dfw5-1.xx&oh=00_AfCsUR4rtRiKh7n5ThYkl_a3KZxsuL_K_bK-2LM783NB0w&oe=640277B3",
    "https://scontent-dfw5-1.xx.fbcdn.net/v/t1.18169-9/24578_1437123605497_5730494_n.jpg?_nc_cat=110&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=5gCRBhJkQrkAX_kj5Fl&_nc_ht=scontent-dfw5-1.xx&oh=00_AfDBO_KVqRfBvH9q1P2ofBbkINGhcSDAN9c3W_rViDRCiw&oe=6402778E",
    "https://scontent-dfw5-1.xx.fbcdn.net/v/t1.18169-9/24578_1437112925230_3699514_n.jpg?_nc_cat=105&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=D0-LuFcvjdAAX810Y88&_nc_ht=scontent-dfw5-1.xx&oh=00_AfAYXN3SGoAXj5NepGYd15SErudHBHGqY3f4K9BJCJrYHQ&oe=64026778",
    "https://scontent-dfw5-2.xx.fbcdn.net/v/t1.18169-9/24578_1437112805227_4313319_n.jpg?_nc_cat=102&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=i8vS0O7LpxUAX8zQo6X&_nc_ht=scontent-dfw5-2.xx&oh=00_AfDKosc1A9APDuR5YA3K-q-2Lyg1PQEOzAzgIVMxw2Lh3A&oe=64027206",
    "https://scontent-dfw5-2.xx.fbcdn.net/v/t1.18169-9/24578_1437112885229_7432120_n.jpg?_nc_cat=104&ccb=1-7&_nc_sid=cdbe9c&_nc_ohc=adTHMgBeghUAX_NXMnl&_nc_ht=scontent-dfw5-2.xx&oh=00_AfBAD9E338iJNeFPpeFTrYQ0UHRDR2yNxiuAyy14ODjhgQ&oe=64028BFE",
]


p_img_url = image_url_list[22]
p_visual_features = 'Description,ImageType,Color,Categories,Objects,Tags,Faces,Brands,Adult'   # 'Description,ImageType,Color,Categories,Objects,Tags,Faces,Brands,Adult' 
p_language = 'en'
p_model_version = 'latest'

print("total images:", len(image_url_list))
print("p_img_url:", p_img_url)
print("p_visual_features:", p_visual_features)
print("p_language:", p_language)
print("p_model_version:", p_model_version)



#%%
# Call Azure Cognitive Services with URL

http_url = f"{endpoint}vision/v3.2/analyze"
http_json = { 'url': p_img_url } 
http_data = None
http_headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Content-Type': "application/json"
    }
http_params = {
    'visualFeatures': f"{p_visual_features}",
    'language':       f"{p_language}",
    'model-version':  f"{p_model_version}",
    }

result = processRequest(http_url, http_json, http_data, http_headers, http_params )

printResultsOnConsole(result)


#%%
# Load Image from URL, add attributes, display

if result is not None:

    arr = np.asarray( bytearray( requests.get( p_img_url ).content ), dtype=np.uint8 )
    img = cv2.cvtColor( cv2.imdecode( arr, -1 ), cv2.COLOR_BGR2RGB )

    img = renderResultOnImage( result, img )

    ig, ax = plt.subplots(figsize=(15, 20))
    ax.imshow( img )



#%%##############################################################################################################################################
# Analysis of an image stored on disk

# Load raw image file into memory
p_path_to_image = r'/home/carlosm/Pictures/Images_for_OCR/readsample_downloaded.jpg'
p_visual_features = 'Description,ImageType,Color,Categories,Objects,Tags,Faces,Brands,Adult'   # 'Description,ImageType,Color,Categories,Objects,Tags,Faces,Brands,Adult' 
p_language = 'en'
p_model_version = 'latest'

print("p_path_to_image:", p_path_to_image)
print("p_visual_features:", p_visual_features)
print("p_language:", p_language)
print("p_model_version:", p_model_version)


#%%
# Call Azure Cognitive Services with local image

http_url = f"{endpoint}vision/v3.2/analyze"
http_json = None 
http_headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Content-Type': "application/octet-stream" 
    }
http_params = {
    'visualFeatures': f"{p_visual_features}",
    'language':       f"{p_language}",
    'model-version':  f"{p_model_version}",
    }

with open(p_path_to_image, 'rb' ) as f:
    http_data = f.read() 

result = processRequest(http_url, http_json, http_data, http_headers, http_params )

printResultsOnConsole(result)


#%%
# Load Image from local file, add attributes, display

if result is not None:

    data8uint = np.fromstring(http_data, np.uint8 ) # Convert string to an unsigned int array
    img = cv2.cvtColor( cv2.imdecode( data8uint, cv2.IMREAD_COLOR ), cv2.COLOR_BGR2RGB )

    img = renderResultOnImage( result, img )

    ig, ax = plt.subplots(figsize=(15, 20))
    ax.imshow( img )


#%%