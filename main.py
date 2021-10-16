### First get input
from apify_client import ApifyClient
import os
import json

# Unfortunately, the env vars are only available on the Apify platform
# For local runs you will have to comment out the client and mock the values
token = os.getenv('API_TOKEN')
apify_client = ApifyClient(token)

# On Apify platform, input is saved in local Key-Value Store as INPUT record
kv_store_id = os.getenv('APIFY_DEFAULT_KEY_VALUE_STORE_ID')
input = json.loads(apify_client.key_value_store(kv_store_id).get_record('INPUT'))
#input = {'image_url': './image1.png', 'lang':'en'}

# You have the input now, do stuff with it
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang=input['lang'], use_gpu=False) # need to run only once to download and load model into memory
img_path = './imgs_en/img_12.jpg'
result = ocr.ocr(input['image_url'], cls=True)

output = {}
i=0
for line in output:
    output[i] = line

output = json.dumps(output)
#print(output)
apify_client.key_value_store(kv_store_id).set_record('OUTPUT', output)